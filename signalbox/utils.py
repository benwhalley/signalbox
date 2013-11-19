#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404
from signalbox.utilities.djangobits import supergetattr


def padleft(thing, n, default=None):
    while len(thing) < n:
        thing.insert(0, default)
    return thing



def get_object_or_none(modelclass, **kwargs):
    try:
        return get_object_or_404(modelclass, **kwargs)
    except Http404:
        return None


def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""

    url = 'http://%s' % (Site.objects.get_current().domain, )
    return url


def in_range(p, range):
    """Check p is between items of range tuple; return boolean."""

    a, b = range
    return bool(a <= p < b)


def execute_the_todo_list(study=None, user=None):
    """Create list of Observations due and do() them"""
    from signalbox.models.observation_timing_functions import observations_due_in_window

    todo = observations_due_in_window()

    if study:
        todo = filter(lambda x: supergetattr(x, 'dyad.study', None) == study, todo)

    if user:
        todo = filter(lambda x: supergetattr(x, 'dyad.user', None) == user, todo)

    return [(i, i.do()) for i in todo]


def send_reminders_due_now(study=None):
    """Create list of ReminderInstances due and do them"""
    from signalbox.models.observation import ReminderInstance
    todo = ReminderInstance.objects.filter(due__lte=datetime.now())
    todo = todo.exclude(sent=True)
    todo = todo.exclude(observation__status=1)
    todo = todo.exclude(observation__dyad__active=False)
    todo = todo.exclude(observation__dyad__study__paused=True)

    return [(i, i.send_reminder()) for i in todo]


def csv_to_list(string):
    if string:
        return [i.strip() for i in string.split(",") if i]
    return []


def incomplete(qset):
    """Accept a queryset of Observations. Return those which are incomplete."""
    overdue = qset.filter(due__lte=datetime.now())
    return overdue.exclude(status=1)


def proportion(n, N):
    if N == 0:
        return 1
    if n == 0:
        return 0
    return n / (N + 0.0)


def percent(n, N):
    return int(proportion(n, N) * 100)


def proportion_tuple(tup):
    n, N = tup
    return proportion(n, N)


def pretty_datetime(dateobj):
    return dateobj.strftime("%H:%M on %a %d %B %Y")
