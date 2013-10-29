#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib import messages
from django.conf import settings
from signalbox.utils import *
from signalbox.models import *
from registration.backends.simple.views import RegistrationView

from signalbox.forms import UserProfileForm

from registration.forms import RegistrationForm
from registration.backends.simple.views import RegistrationView
from django import forms


class SignalboxRegistrationForm(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds fields per-study.
    """
    study = forms.ModelChoiceField(queryset=Study.objects.all(), required=True, widget=forms.HiddenInput())


class SignalboxRegistrationView(RegistrationView):
    """
    Custom registration view that uses our custom form.

    """
    form_class = SignalboxRegistrationForm

    def get_study(self):
        return get_object_or_404(Study, pk=self.kwargs.get('study_id'))

    def get_initial(self):
        return {'study': self.get_study()}

    def get_context_data(self, **kwargs):
        context = super(SignalboxRegistrationView, self).get_context_data(**kwargs)
        context['study'] = self.get_study()
        return context

    def register(self, request, *args, **kwargs):
        study = self.get_study()
        user = super(SignalboxRegistrationView, self).register(request, *args, **kwargs)

        return user

    def get_success_url(self, request, newuser):

        return reverse('join_study', args=(self.get_study().id,))
        return "/"


def _add_user_to_study(request, user, study):
    try:
        dyad, created = Membership.objects.get_or_create(user=user, study=study)
        if created:
            messages.success(request, study.welcome_text)
        else:
            messages.error(request,
                    "You were already registered for this study (%s)" % (study.name))

        return dyad

    except Membership.MultipleObjectsReturned:
        messages.error(request, "You were already registered for this study (%s)" % (study.name))


def update_profile_for_studies(request, study_pk):

    form = UserProfileForm(request.POST or None, instance=request.user.get_profile(), request=request)

    if form.is_valid():
        form.save()
        messages.info(request, "Personal details updated.")
        _ = execute_the_todo_list(user=request.user)
        return HttpResponseRedirect(reverse('user_homepage'))

    return render_to_response('signalbox/additional_info.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def join_study(request, pk):
    study = get_object_or_none(Study, id=pk)

    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('study_registration', args=(study.id,)))

    membership = _add_user_to_study(request, request.user, study)

    if not request.user.get_profile().has_all_required_details():
        return HttpResponseRedirect(reverse('update_profile_for_studies', args=(study.id,)))

    if not study:
        return HttpResponseRedirect(reverse('study'))

    return HttpResponseRedirect(reverse('user_homepage'))


@login_required
def user_homepage(request):
    """Just returns the request to the template.

    This makes the User available to the template as {{user}} which  is used to
    output relevant details for them."""

    if not request.user.get_profile().has_all_required_details():
        return HttpResponseRedirect(reverse('update_profile_for_studies'))

    return render_to_response('signalbox/user_home.html',
                              {},
                              context_instance=RequestContext(request))


class MembershipDetail(DetailView):
    """Class based view of Memberships to be used on the frontend."""
    model = Membership

    def get_object(self):
        obj = super(MembershipDetail, self).get_object()
        if obj.user == self.request.user:
            return obj
        else:
            raise Http404
