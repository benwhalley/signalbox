from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^outbound/initialise/(?P<observation_token>[\w-]+)/$',
        views.initialise_call, {}, "initialise_call"),
    url(r'^outbound/call/reply/(?P<reply_token>[\w-]+)/question/(?P<question_index>[\d+])/$', views.play, {}, "play" ),
    url(r'^inbound/call/?$', views.answerphone, {}, "answerphone"),
    url(r'^inbound/sms/$', views.sms_callback, {}, "sms_callback"),
]
