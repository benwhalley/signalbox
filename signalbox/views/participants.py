#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import messages
import django.http as http
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from signalbox.split_select_date_time_widget import SplitSelectDateTimeWidget
from signalbox.models import *
from signalbox.forms import *
from signalbox.decorators import group_required


def awaiting_followup(user):
    """Checks whether a ContactRecord is expected Returns a boolean.

    ContactReasons can indicate that a followup record is expected - for
    example, if a letter is sent then we would want to be able to flag
    users where this hasn't been followed up. This function checks
    whether the last ContactRecord requires a followup.
    """

    contacts = user.contactrecord_set.all()
    if contacts.count() > 0:
        last_contact = contacts[0]
        if last_contact.reason and last_contact.reason.followup_expected:
            return True
    return False


@group_required(['Researchers', 'Clinicians', 'Assessors', 'Research Assistants'])
def show_followups_outstanding(request):
    """Display a list of users needing a followup."""

    # yuck, we query for each user separately, but this isn't a public view
    everyone = [i for i in User.objects.all() if awaiting_followup(i)]

    return render_to_response('manage/followups_outstanding.html',
                              {'users': everyone, }, RequestContext(request))


@group_required(['Researchers', 'Clinicians', 'Assessors', 'Research Assistants', ])
def find_participant(request):
    form = FindParticipantForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.cleaned_data['participant']
        return HttpResponseRedirect(reverse('participant_overview', args=(str(user.id),)))
    return render_to_response('manage/find_participant.html',
                              {'form': form, }, RequestContext(request))


@group_required(['Researchers', 'Clinicians', 'Research Assistants', 'Assessors'])
def participant_overview(request, pk):

    user = participant = get_object_or_404(User, pk=pk)

    contactrecordform = ShortContactRecordForm(request.POST or None)
    messageform = UserMessageForm(request.POST or None,
                                  initial={'message_to': user, 'message_type': 'SMS', })

    if request.POST and contactrecordform.is_valid():
        rec = contactrecordform.save(commit=False)
        rec.participant = user
        rec.added_by = request.user
        rec.save()
        messages.success(request, "Contact note saved")
        return HttpResponseRedirect(reverse('participant_overview', args=(user.id, )))

    return render_to_response('manage/participant_overview.html', {
        'participant': participant,
        'contactrecordform': contactrecordform,
        'messageform': messageform
    }, RequestContext(request))


@group_required(['Researchers', 'Clinicians', 'Research Assistants' ])
def edit_participant(request, pk):
    """Displays and manages 2 forms to edit participants."""

    participant = None
    user = get_object_or_404(User, pk=pk)
    try:
        pform = UserProfileForm(
            request.POST or None, instance=user.get_profile(), request=request)
    except UserProfile.DoesNotExist:
        pform = UserProfileForm(
            request.POST or None, instance=UserProfile(user=user), request=request)

    title = "Edit participant"

    if pform.is_valid():
        pform.save()
        messages.success(request, "Details for %s saved." % user.username)
        return http.HttpResponseRedirect(reverse('participant_overview', args=(user.id, )))

    return render_to_response('manage/edit_participant.html',
          {'form': pform, 'title': title, 'user': user}, RequestContext(request))
