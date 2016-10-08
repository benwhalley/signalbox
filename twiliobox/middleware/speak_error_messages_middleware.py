from django.shortcuts import render
from twiliobox.exceptions import TwilioBoxException
from twiliobox.question_methods import reply_to_twilio, say_or_play_phrase
from django.http import HttpResponse
from twilio import twiml


class SpeakErrorMessagesMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, TwilioBoxException):
            return reply_to_twilio(
                say_or_play_phrase(twiml.Response(), str(exception))
            )
