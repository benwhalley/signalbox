import json
import urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from question_methods import say_extra_text, reply_to_twilio
from reversion import revision
from signalbox.models import Observation, Reply, Answer, TextMessageCallback
from signalbox.utilities.djangobits import conditional_decorator
from signalbox.utilities.more_itertools import first
from signalbox.utils import current_site_url
from twilio import twiml
from twiliobox.exceptions import TwilioBoxException
from twiliobox.models import TwilioNumber
from contracts import contract

@csrf_exempt
@contract
def initialise_call(request, observation_token):
    """Accept inbound POST from Twilio, make a Reply and redirect to play.
    :type request: a
    :type observation_token: string
    :rtype: b
    """

    observation = get_object_or_404(Observation, token=observation_token)
    observation.make_reply(request, entry_method="twilio",
        external_id=request.POST.get('CallSid', None))
    url = current_site_url() + reverse('play', args=(reply.token, 0))
    return HttpResponseRedirect(url)


@contract
def get_question(questions, index):
    """
    :type questions: list
    :type index: int
    :rtype: b|None
    """
    if index < 0:
        return None
    try:
        return questions[index]
    except IndexError:
        return None


@conditional_decorator(revision.create_on_success, settings.USE_VERSIONING)
def save_answer(reply, question, querydict):
    """Takes a Reply, a question and the POST dict and returns a (saved) answer."""

    # twilio returns a list of digits, but we only take the first
    user_answer = first(querydict.getlist('Digits'), "")
    extra_json = json.dumps(querydict, sort_keys=True, indent=4)

    # if versioning is off we need to delete any previous answers before trying
    # to create this one because answers can't be modified (but can be deleted)
    prev_answers = Answer.objects.filter(reply=reply, question=question, page=question.page)
    if not settings.USE_VERSIONING and prev_answers.count():
        prev_answers.delete()

    answer, created = Answer.objects.get_or_create(reply=reply, question=question, page=question.page)
    answer.answer = user_answer
    answer.meta = extra_json,
    answer.choices = question.choices_as_json()
    answer.save(force_save=True) # force save because answer may be readonly if versioning off
    return answer


def _lookup_asker_for_inbound_number(numberstring):
    number = TwilioNumber.objects.get(
        phone_number__icontains=numberstring.replace("+", ""))
    return number.answerphone_script


@csrf_exempt
def play(request, reply_token, question_index=0):
    """Rewritten controller to present Twiml for each question and save responses."""

    question_index = int(question_index)
    reply = Reply.objects.get(token=reply_token)
    if not reply:
        return reply_to_twilio(say_extra_text(twiml.Response(),
            "No reply found for this token."))
    asker = reply.asker

    # # ---- tmp for testing
    # from ask.models import Asker
    # reply = Reply()
    # reply.asker = Asker.objects.get(id=42)
    # asker = reply.asker or reply.observation.created_by_script.asker
    # reply.save()
    # # ---- endtmp

    repeat_url = current_site_url() + reverse('play', args=(reply.token, question_index))
    questions = [i for i in asker.questions() if i.showme(reply)]
    prev_question = get_question(questions, question_index - 1)
    try:
        thequestion = questions.pop(question_index)
    except IndexError:
        raise TwilioBoxException("There is no question {}".format(question_index))

    # import ipdb; ipdb.set_trace()
    if request.POST and prev_question:
        answer = save_answer(reply, prev_question, request.POST)
        was_suitable = prev_question.check_telephone_keypad_answer(answer.answer)

        if was_suitable:
            if thequestion.index() + 1 == len(questions):
                # mark the observation and reply as complete because the last
                # question is required to be a hangup type which doesn't collect
                # any data xxx todo add hangup if last q is not hangup to asker
                _ = reply.observation and reply.observation.update(1)
                _ = reply.finish(request)
                # then drop through to play the last question

            return HttpResponseRedirect(
                current_site_url() +
                reverse('play', args=(reply.token, question_index + 1))
            )

        # if the user responds with a * then repeat the question again
        elif answer.answer == "*":
            response = twiml.Response()
            say_extra_text(response, "Repeating the question")
            response.redirect(url=repeat_url, method="POST")
            return reply_to_twilio(response)

        else: # wasn't a suitable response
            response = twiml.Response()
            say_extra_text(response, "Sorry, {} wasn't a suitable answer.")
            response.redirect(url=repeat_url, method="POST")
            return reply_to_twilio(response)


    vfun = thequestion.field_class()(thequestion, reply, request).voice_function
    return reply_to_twilio(
        vfun(twiml.Response(), thequestion, reverse("play", args=(reply.token, question_index+1, )), reply)
    )



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

