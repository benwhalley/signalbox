#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template import RequestContext, Context, Template, loader
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import *
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, backends

from signalbox.utilities.djangobits import get_object_from_queryset_or_404
from signalbox.utilities.error_views import render_forbidden_response
from signalbox.decorators import group_required

from signalbox.models import Script, Membership, Observation, Reply, ScoreSheet
from ask.models import Asker


def start_data_entry(request, observation_token, success_url=None,
                                            entry_method=None, *args, **kwargs):
    """
    Lookup observation, make reply, login(?), redirect to the Questionnaire.


    Note, checks are made to ensure data only entered for observations while
    they are 'open'. IF LOGIN_FROM_OBSERVATION_TOKEN is True, some types of
    users will be automatically logged in if the url contains a valid
    observation token.
    """

    observation = get_object_or_404(Observation, token=observation_token)
    ok_to_start, message = observation.open_for_data_entry(request)

    if not ok_to_start:
        messages.add_message(request, messages.INFO, message)
        return HttpResponseRedirect(reverse('user_homepage'))

    # Allows us to log users in from an email token
    theuser = observation.dyad.user
    prof = theuser.get_profile()
    if settings.LOGIN_FROM_OBSERVATION_TOKEN and prof.can_login_from_observation_token():
        theuser.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, theuser)

    success_url = success_url or request.GET.get('success_url', None)

    reply = observation.make_reply(request,
                                   entry_method=entry_method,
                                   success_url=success_url)

    # If we are redirecting to an external provider like SurveyMonkey
    # then do it here.

    if observation.created_by_script.external_asker_url:
        observation.status = -4  # status for 'redirected to external service'
        observation.save()
        return HttpResponseRedirect(
            observation.created_by_script.parse_external_asker_url(reply))

    # Otherwise start entering data
    return HttpResponseRedirect(reverse('show_page', kwargs={'reply_token': reply.token}))


@login_required
def use_ad_hoc_script(request, membership_id, script_id):

    membership = get_object_or_404(Membership, id=membership_id)
    script = get_object_or_404(Script, id=script_id)

    assert script in membership.study.ad_hoc_scripts.all(), \
        "Script not available for use by this study."

    entering_for_self = request.user == membership.user

    assert request.user.is_staff or entering_for_self, \
        "User not staff and not entering data for herself."

    observations = script.make_observations(membership=membership)
    observations = sorted(
        observations, key=operator.attrgetter('due_original'))
    first_ob = observations[0]


    if entering_for_self:
        return_url = reverse('user_homepage', args=None)
    else:
        return_url = reverse('participant_overview', args=(membership.user.id, ))

    return start_data_entry(request,
                            first_ob.token,
                            return_url,
                            "Ad hoc script")


@group_required(['Researchers', 'Clinicians', 'Research Assistants', ])
def preview_reply(request, id):
    """Display information about a Reply a participant has made.

    NOTE - it is only possible to view replies to scripts designated as for screening
    purposes in this way - outcome data should not be displayed."""

    reply_exists = Reply.objects.filter(id=id).count() > 0

    reply = reply_exists and get_object_from_queryset_or_404(
        Reply.objects.authorised(request.user), id=id
    )

    if reply_exists and not reply:
        raise PermissionDenied(
            "Your account doesn't have access to that page. Login as a different user?")

    scoresheets = reply.asker.scoresheets()
    scores = [(i, i.compute(reply.answer_set.all())) for i in scoresheets]

    return render_to_response('manage/preview_reply.html',
                              {'reply': reply, 'scores': scores},
                              context_instance=RequestContext(request)
                              )
