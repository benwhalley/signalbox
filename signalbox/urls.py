#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

'''
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.defaults import url, patterns
from django.contrib.auth.views import logout
from django.http import HttpResponseForbidden
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic import RedirectView
from signalbox.forms import CreateParticipantForm, UserProfileForm, ParticipantPasswordForm
from signalbox.models import Study
from signalbox.views.assessors import observations_outstanding
from signalbox.views.back import *
from signalbox.views.data import *
from signalbox.views.front import join_study, user_homepage, MembershipDetail, update_profile_for_studies, SignalboxRegistrationView
from signalbox.views.participants import *
from signalbox.views.replies import *
from signalbox.views.usermessage import send_usermessage
from signalbox.utilities.extra_content_view import ExtraContextView

from tastypie.api import Api
import ask.api
v1_api = Api(api_name='v1')
v1_api.register(ask.api.ChoiceSetResource())
v1_api.register(ask.api.AskerResource())


# Other signalbox apps

urlpatterns = patterns('',
        (r'^ask/', include('ask.urls')),
        (r'^admin/ask/', include('ask.urls_admin')),
        (r'^twilio/', include('twiliobox.urls')),
        (r'^selectable/', include('selectable.urls')),
        (r'^api/', include(v1_api.urls)),
)

# FRONTEND URLS

urlpatterns = urlpatterns + patterns('',
    url(r'^enter/data/(?P<observation_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})/?$',
        start_data_entry, {'entry_method': "participant"}, name="start_data_entry"),

    url(r'^double/enter/data/(?P<observation_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})/?$',
        start_data_entry, {'entry_method': "double_entry"},
        name="start_double_entry"),

    url(r'^studies/$',
        ListView.as_view(model=Study, queryset=Study.objects.filter(visible=True, paused=False)),
        name='study_list'),

    url(r'^studies/(?P<pk>\d+)/$', DetailView.as_view(model=Study,), {}, name='study', ),
    url(r'^studies/(?P<pk>\d+)/join/$', join_study, name='join_study'),
    url(r'^studies/(?P<study_id>\d+)?/register/$', SignalboxRegistrationView.as_view(), name='study_registration'),

    url(r'^add/participant/details/(?P<study_pk>\d+)?/?$',
        update_profile_for_studies, name='update_profile_for_studies'),

    url(r'^accounts/profile/membership/(?P<pk>\d+)$',
        MembershipDetail.as_view(), {}, name='membership_home', ),

    url(r'^profile/$', RedirectView.as_view(url='accounts/profile/')),
    url(r'^accounts/profile/?$', user_homepage, name='user_homepage'),

    url(r'^logout/?$', logout, {'next_page': '/'}, name='logout'),

    url(r'^crossdomain.xml$', lambda x: HttpResponseForbidden("Forbidden")),
)




# ADMIN URLS

class AdminMessageView(ExtraContextView):
    template_name = "admin/message.html"


urlpatterns = urlpatterns + patterns('',
    url(r'^cron/$', do_outstanding_observations, {}, 'cron' ),

    url(r'^answer/(?P<pk>\d+)/upload/$', AnswerFileView.as_view(), {}, 'user_uploaded_file' ),

    # assessor views
    url(r'^observations/outstanding/$', observations_outstanding, {}, "observations_outstanding"),

    url(r'^membership/(?P<pk>\d+)/todo/$', ObservationView.as_view(), {}, "membership_observations_todo"),
    url(r'^reply/(?P<pk>\d+)/check/double/entry/$', ReplyUpdateAfterDoubleEntry.as_view(), {}, "check_double_entry"),

    # this overrides adding observations in the admin
    url(r'^observation/add/?$', AdminMessageView.as_view(extra_context=
            {'message': """You can't add extra observations manually."""}), ),

    # some reporting views
    url(r'^followups/outstanding/?$', show_followups_outstanding, {}, "show_followups_outstanding"),


    # user messages
    url(r'^email/new/(?P<username>\w+)?/?$', send_usermessage, {'message_type': 'Email'}, "send_user_email"),
    url(r'^sms/new/(?P<username>\w+)?/?$', send_usermessage, {'message_type': 'SMS'}, "send_user_sms"),


    # preview timings for scripts / conditions
    url(r'^timings/studycondition/preview/(?P<pk>\d+)/$', preview_timings, {'klass': "StudyCondition"}, "preview_studycondition_timings"),
    url(r'^script/preview/(?P<pk>\d+)/$', preview_timings, {'klass': "Script"}, "preview_script"),
    url(r'^preview/timings/$', preview_timings_as_txt, {}, "preview_timings_as_txt"),


    # view called via jquery for instant previews of the script message
    url(r'^script/message/preview/$', script_message_preview, {}, "script_message_preview"),


    # main filter view for observations
    # url(r'^observations/$', list_obs, {}, "list_obs"),

    # custom add and edit participants
    url(r'^participant/new/$',
        NewParticipantWizard([CreateParticipantForm, ParticipantPasswordForm]), {}, 'new_participant'),

    url(r'^participant/(?P<user_id>\d+)/reset/password/$', send_password_reset, {}, "send_password_reset"),
    url(r'^participant/(?P<pk>\d+)/edit/$', edit_participant, {}, 'edit_participant'),
    url(r'^participant/find/$', find_participant, {}, 'find_participant'),
    url(r'^participant/(?P<pk>\d+)/$', participant_overview, {}, 'participant_overview'),


    # membership functions
    url(r'^membership/dateshift/(?P<pk>\d+)/$', dateshift_membership, {}, 'dateshift_membership'),
    url(r'^membership/(?P<membership_id>\d+)/use/script/(?P<script_id>\d+)/$',
        use_ad_hoc_script, {}, 'use_ad_hoc_script'),


    # showing observations outstanding and resending
    url(r'^todo/$', show_todo, {}, 'show_todo'),
    url(r'^todo/do/$', do_todo, {}, 'do_todo'),
    url(r'^resend/(?P<obs_id>\d+)/$', resend_observation_signal, {}, 'resend_observation_signal'),


    # have a look at replies
    url(r'^reply/preview/(?P<id>\d+)/$', preview_reply, {}, "preview_reply"),

    # resolving duplicate replies
    url(r'^resolve/duplicate/replies/$', resolve_double_entry_conflicts, {}, 'resolve_double_entry_conflicts'),
    url(r'^resolve/duplicate/replies/(?P<study_id>\d+)/$', resolve_double_entry_conflicts, {}, 'resolve_double_entry_conflicts_for_study'),
    url(r'^resolve/duplicate/replies/observation/(?P<observation_id>\d+)/$', resolve_double_entry_conflicts, {}, 'resolve_double_entry_conflicts_for_observation'),
    url(r'^reply/mark/canonical/(?P<reply_id>\d+)/?$', mark_reply_as_canonical, {}, 'mark_reply_as_canonical'),
    url(r'^reply/unmark/canonical/(?P<reply_id>\d+)/?$', mark_reply_as_canonical, {'set_to': False}, 'unmark_reply_as_canonical'),

    # exporting data
    url(r'^export/study/data/$',
        export_data, {}, "export_data"),

    url(r'^addobs/(?P<membership_id>\d+)/$',
        add_observations_for_membership, name="add_observations_for_membership"),

    url(r'^randomise/(?P<membership_id>\d+)/$',
        randomise_membership, name="randomise_membership"),

    url(r'^create/membership/(?P<user_id>\d+)?/?$',
        add_participant, name="create_membership"),

    url(r'^user/password/$', 'django.contrib.auth.views.password_change')

)


if settings.USE_VERSIONING:
    # checking revisions
    urlpatterns += (url(r'^history/$', VersionView.as_view(), {}, "check_history"),)
