#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines receiver functions for a number of post-save hooks, including adding
observations and allocating memberships to StudyConditions automatically, if
required by the Study. See https://docs.djangoproject.com/en/dev/topics/signals/

"""
from __future__ import print_function

from functools import wraps
import itertools
import logging
import sys
import traceback

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from registration.signals import user_registered
from signalbox.allocation import allocate
from signalbox.models import (Reply, Observation, Membership, 
    UserProfile, TextMessageCallback, Alert, AlertInstance)
from signalbox.signals import sbox_anonymous_reply_complete
from signalbox.utils import execute_the_todo_list

logger = logging.getLogger(__name__)


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
            print("Alert triggered for reply {} but not sending another message".format(
                reply.id), file=sys.stderr)
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
        # we don't execute at this point if we are testing because it makes unit
        # tests awkward (we can't test the intermediate states of some functions.)
        if not settings.TESTING:
            execute_the_todo_list()


@receiver(sbox_anonymous_reply_complete, sender=Reply)
def send_email_after_anonymous_asker(sender, **kwargs):
    reply = kwargs.get('reply')
    request = kwargs.get('request')
    subject = "Signalbox: Anonymous reply made to {}".format(reply.asker)
    url = request.build_absolute_uri(reverse('admin:signalbox_reply_change', args=(reply.id,)))
    body = """Anonymous reply made to {} at {}. {}""".format(reply.asker, reply.last_submit, url)
    try:
        send_mail(subject, body, "no-reply@thesignalbox.net", settings.DATA_ADMINS, fail_silently=False)
    except SMPTException:
        logger.error("Could not send email\n"+traceback.format_exc())


