"""Public-facing urls for the ask app."""

from ask.views import preview_asker, show_page, start_anonymous_survey
from django.conf.urls import url
from signalbox.views.replies import *

urlpatterns = [
    url(r'^preview/q/(?P<asker_id>\d+)?/(?P<page_num>\d+)?/$', preview_asker,
        name="preview_asker"),
    url(r'^(?P<reply_token>[\w-]+)/$', show_page, {'preview': False},
        name="show_page"),
    url(r'^q/(?P<asker_id>\d+)/(?P<collector>[\w\-\_]+)?/?$', start_anonymous_survey,
        name="start_anonymous_survey"),
]
