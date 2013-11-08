from ask.views import preview_asker, show_page, start_anonymous_survey
from django.conf.urls import patterns, url
from signalbox.views.replies import *



# FRONTEND PATTERNS

urlpatterns = patterns('',
    url(r'^preview/(?P<asker_id>\d+)?/(?P<page_num>\d+)?/$', preview_asker,
        name="preview_asker"),
    url(r'^(?P<reply_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$', show_page, {'preview': False },
        name="show_page"),
    url(r'^anon/(?P<asker_id>\d+)/(?P<collector>[\w\-\_]+)?/?$', start_anonymous_survey,
            name="start_anonymous_survey"),
)


