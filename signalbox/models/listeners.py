#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines receiver functions for a number of post-save hooks, including adding
observations and allocating memberships to StudyConditions automatically, if
required by the Study. See https://docs.djangoproject.com/en/dev/topics/signals/

"""
import sys
import itertools
from django.db.models import Q
from django.dispatch import receiver, Signal

from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from registration.signals import user_registered

from signalbox.allocation import allocate
from signalbox.models import Reply, Observation, Membership, UserProfile, \
    TextMessageCallback, Alert, AlertInstance
from signalbox.utils import execute_the_todo_list

from functools import wraps


def disable_for_loaddata(signal_handler):
    """Turn off signal handlers when loading fixture data.

    This is needed when importing a serialised version of the DB becauase
    otherwise we will see IntegrityErrors because of missing objects part-way
    through the process.

    Note, this decorator needs to come after the @receiver decorator.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get('raw', None):
            return
        signal_handler(*args, **kwargs)
    return wrapper


@receiver(post_save, sender=Reply, dispatch_uid="signalbox.listeners")
@disable_for_loaddata
def create_observations_in_response_to_user_answers(sender, instance, created, **kwargs):
    """Listen for replies saved; Check if any atached Answers should create new Observations.
    If they do, create them and call their do() method.
    """
    if instance.observation and instance.observation.dyad:
        rules = instance.observation.dyad.study.createifs.all()
        new_obs = [i.make_new_observations(instance) for i in rules]
        new_obs = itertools.chain(*new_obs)
        [i.do() for i in new_obs]


def _check_alert_and_save_alertinstance(alert, reply):
    meetscriteria = alert.condition.evaluate(reply)
    alertcount = reply.alertinstance_set.all().count()

    if meetscriteria:
        if alertcount > 0:
            print >> sys.stderr, "Alert triggered for reply {} but not sending another message".format(
                reply.id)
            return

        ai = AlertInstance(reply=reply, alert=alert)
        ai.save()
        ai.do()
        return ai


@receiver(post_save, sender=Reply, dispatch_uid="signalbox.listeners")
@disable_for_loaddata
def check_answers_and_make_alerts(sender, instance, created, **kwargs):
    """Listen for replies saved; Check if any alerts for this study are triggered.
    Save alert instances if needed.
    """
    if not instance.observation and instance.observation.dyad:
        return
    alertrules = instance.observation.dyad.study.alerts.all()
    return [_check_alert_and_save_alertinstance(a, reply) for a in alertrules]


@receiver(post_save, sender=User, dispatch_uid="signalbox.listeners")
@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    """Create a userprofile for a new user if not already created."""

    if created is True:
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        profile.save()


@receiver(user_registered, dispatch_uid="signalbox.listeners")
@disable_for_loaddata
def setup_profile(request, user, **kwargs):
    """Create a UserProfile.
    """

    profile, new = UserProfile.objects.get_or_create(user=user)
    profile.save()


@receiver(post_save, sender=Observation, dispatch_uid="signalbox.listeners.jitter")
@disable_for_loaddata
def add_jitter(sender, created, instance, **kwargs):
    """If a script specifies Jitter, then add the requisite noise +/- on to the due time."""
    if created and instance.created_by_script and instance.created_by_script.jitter:
        instance.add_jitter(instance.created_by_script.jitter)
        instance.save()


user_input_received = Signal(providing_args=["reply"])


@receiver(user_input_received)
@disable_for_loaddata
def update_completion_status(sender, reply, **kwargs):
    """Denormalises information from the completion_data() function on save.

    TODO: This is useful in the admin, for sorting etc, but it might end up as a
    bit of a performance problem on the frontend, so keep an eye on it.
    """
    if not reply.observation:
        return False

    n, _, incomple = reply.observation.completion_data()
    if n is not None:
        reply.observation.n_questions = n
        reply.observation.n_questions_incomplete = incomple


@receiver(post_save, sender=Observation, dispatch_uid="signalbox.listeners.reminders")
@disable_for_loaddata
def add_reminders(sender, created, instance, **kwargs):
    """If a script specifies Reminders, then add the ReminderInstances here."""
    if created:
        instance.add_reminders()


@receiver(post_save, sender=Membership, dispatch_uid="signalbox.listeners")
@disable_for_loaddata
def allocate_new_membership(sender, created, instance, **kwargs):
    """When a participant joins a study, we need to randomise them and add observations
    if the Study settings say so."""

    if created and instance.study.auto_randomise:
        _, _ = allocate(instance)

    if created and instance.study.auto_add_observations and instance.study.auto_randomise:
        instance.add_observations()
        # XXX TODO decide whether to execute at this point... it makes testing awkward,
        # but would speed up callbacks to mobiles. Would be better done as a queue system though.
        # execute_the_todo_list()
