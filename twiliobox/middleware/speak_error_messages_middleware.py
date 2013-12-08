from django.template import RequestContext
from django.shortcuts import render_to_response
from twiliobox.exceptions import TwilioBoxException
from twiliobox.question_methods import reply_to_twilio, say_extra_text
from django.http import HttpResponse
from twilio import twiml


class SpeakErrorMessagesMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, TwilioBoxException):
            return reply_to_twilio(say_extra_text(twiml.Response(),
                str(exception)))
