from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^outbound/initialise/(?P<observation_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})/$',
        views.initialise_call, {}, "initialise_call"),
    url(r'^outbound/call/reply/(?P<reply_token>[\w]{8}(-[\w]{4}){3}-[\w]{12})/question/(?P<question_index>[\d+])/$', views.play, {}, "play" ),
    url(r'^inbound/call/?$', views.answerphone, {}, "answerphone"),
    url(r'^inbound/sms/$', views.sms_callback, {}, "sms_callback"),
)
