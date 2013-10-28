import urllib
import urlparse
from urllib import urlencode
from signalbox.utilities.more_itertools import first
import json
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from twilio import twiml
from reversion import revision
from signalbox.utils import current_site_url
from django.conf import settings
from django.contrib.auth.models import User
from signalbox.models import Observation, Reply, Answer, TextMessageCallback
from ask.models import Asker
from twiliobox.models import TwilioNumber
from signalbox.utilities.djangobits import conditional_decorator
from question_methods import say_extra_text


@csrf_exempt
def initialise_call(request, observation_token):
    """Accept inbound POST from Twilio, make a new Reply and redirect to view showing Twiml."""

    observation = get_object_or_404(Observation, token=observation_token)
    observation.make_reply(request, entry_method="twilio",
        external_id=request.POST.get('CallSid', None))
    url = current_site_url() + reverse('play_twiml_firstq') + "?" + \
        urllib.urlencode({'CallSid': request.POST.get('CallSid', None)})
    return HttpResponseRedirect(url)


def question_is_last(questions, number):
    return len(questions) - 1 == number


def get_question(questions, index):
    try:
        return questions[index]
    except IndexError:
        return None

from signalbox.decorators import print_all_exceptions


@csrf_exempt
def answerphone(request):
    """Twiml application view which services incoming calls from Twilio."""

    anonymous_user, created = User.objects.get_or_create(username="AnonymousUser")
    call_data_fields = ["From", "Called", "CallSid", "AccountSid"]
    blob = request.POST or request.GET
    incoming_data = {i: blob.get(i, None) for i in call_data_fields}
    incoming = urllib.unquote(incoming_data['Called']).replace("+", "")
    twilio_number = TwilioNumber.objects.get(phone_number__icontains=incoming)
    asker = twilio_number.answerphone_script


    reply = Reply(
        asker=asker,
        external_id=incoming_data['CallSid'],
        user=anonymous_user,
        entry_method="answerphone"
    )
    reply.save()

    # save some details of the call right away as Answers attached to the Reply
    answers = [Answer(reply=reply, other_variable_name=i, answer=j)
        for i, j in incoming_data.items()]
    [i.save() for i in answers]

    return play_twiml(request, first=True, external_id=incoming_data['CallSid'])


@conditional_decorator(revision.create_on_success, settings.USE_VERSIONING)
def save_answer(reply, question, querydict):
    """Takes a Reply, a question and the POST dict and returns a (saved) answer."""

    user_answer = first(querydict.getlist('Digits'), "")
    extra_json = json.dumps(querydict, sort_keys=True, indent=4)
    answer, created = Answer.objects.get_or_create(reply=reply, question=question, page=question.page)
    answer.answer = user_answer
    answer.meta = extra_json,
    answer.choices = question.choices_as_json()
    answer.save()

    return answer


def _lookup_asker_for_inbound_number(numberstring):
    number = TwilioNumber.objects.get(phone_number__icontains=numberstring.replace("+", ""))
    return number.answerphone_script


@csrf_exempt
def play_twiml(request, first, external_id=None):
    """Controller to present Twiml for each question and save responses."""

    external_id = external_id or request.POST.get('CallSid', None) or request.GET.get('CallSid', None)

    if not external_id:
        raise Http404

    # take the most recent
    reply = Reply.objects.filter(external_id=external_id)[0]

    asker = reply.asker or reply.observation.created_by_script.asker
    all_questions = asker.questions()
    the_question = get_question(all_questions, reply.twilio_question_index)
    prev_question = get_question(all_questions, reply.twilio_question_index - 1)
    is_last = question_is_last(all_questions, reply.twilio_question_index)
    twimlresponse = twiml.Response()
    url = current_site_url() + reverse('play_twiml') + "?" + urlencode({'CallSid': external_id})

    if request.POST and prev_question:
        answer = save_answer(reply, prev_question, request.POST)

        # if the user responds with a * then repeat the question again
        if answer.answer == "*":
            the_question = prev_question
            return HttpResponseRedirect(url)

        # also repeat the question if the response is not in the allowed
        # list... Also play an extre message to explain.
        # todo... allow this message to be recorded and added to an asker
        user_made_suitable_response = prev_question.check_telephone_keypad_answer(
            answer.answer
        )
        if not user_made_suitable_response:
            twimlresponse = say_extra_text(twimlresponse, "Sorry, I didn't understand that.")
            the_question = prev_question  # play the previous question again

    field = the_question.field_class()(question=the_question, reply=reply, request=request)

    if is_last:
        twimlresponse = field.voice_function(twimlresponse, the_question, url=url, reply=reply)
        reply.observation and reply.observation.update(1)  # mark the reply as complete
        reply.finish(request)

    else:
        twimlresponse = field.voice_function(twimlresponse, the_question, url=url, reply=reply)
        reply.twilio_question_index += 1
        reply.save()

    return HttpResponse(str(twimlresponse), content_type="text/xml")


TWILIO_SMS_FIELDS = "sid Date_Created Date_Updated Date_Sent Account_Sid From_ To Body \
Status Direction Price Api_Version Uri".lower().split(" ")

TWILIO_CALL_FIELDS = "Sid Parent_Call_Sid Date_Created Date_Updated Account_Sid To From \
Phone_Number_Sid Status Start_Time End_Time Duration Price Direction Answered_By \
Forwarded_From Caller_Name Uri".lower().split(" ")

TWILIO_FIELDS = set(TWILIO_CALL_FIELDS).union(TWILIO_SMS_FIELDS)


def get_from_post_or_get(request, key):
    return request.POST.get(key, None) or request.GET.get(key, None)


@csrf_exempt
def sms_callback(request):
    """Accept SMS callbacks from Twilio.
    """

    sid = get_from_post_or_get(request, 'SmsSid')

    callbackrecord, created = TextMessageCallback.objects.get_or_create(sid=sid, post=json.dumps(request.POST))
    callbackrecord.save()
    return HttpResponse(str(callbackrecord))
