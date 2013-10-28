from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',

    url(r'^initialise/(?P<observation_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$',
        views.initialise_call, {}, "initialise_call"),

    url(r'^twiml/first/?$',
        views.play_twiml, {'first': True }, "play_twiml_firstq"),

    url(r'^twiml/$', views.play_twiml, {'first': False}, "play_twiml" ),

    url(r'^answerphone/?$', views.answerphone, {}, "answerphone"),

    url(r'^sms/callback/$', views.sms_callback, {}, "sms_callback"),

)
