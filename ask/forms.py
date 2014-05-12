"""Forms for the Ask application"""

import os
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ask.models import Question, ChoiceSet, AskPage
from signalbox.models import Answer
from django.conf import settings
import floppyforms as forms
from signalbox.models.listeners import user_input_received
from ask.models.fields import FIELD_NAMES
from django.utils.encoding import smart_unicode
import ask.validators as valid
from ask.utils import statify
from twilio import twiml

if settings.USE_VERSIONING:
    from reversion import revision


class PageForm(forms.Form):
    """Dynamically generated form, from the list of questions in **kwargs."""

    def save(self, *args, **kwargs):

        reply = kwargs.pop('reply')
        page = kwargs.pop('page')
        for key, val in self.cleaned_data.iteritems():
            save_question_response(val, reply, page, variable_name=key)

        # broadcast a signal
        user_input_received.send(self, reply=reply)

        return True

    def __init__(self, *args, **kwargs):
        """Overridden to dynamically create form."""

        reply = kwargs.pop('reply')
        page = kwargs.pop('page')
        request = kwargs.pop('request')

        if page:
            self.questions_to_show = page.get_questions(reply)
        else:
            self.questions_to_show = kwargs.pop('questions')

        super(PageForm, self).__init__(*args, **kwargs)

        for question in self.questions_to_show:
            self.fields[question.variable_name] = question.field_class()(
                question=question,
                reply=reply,
                request=request
            )

        if page:
            self.questions = [{'question': question, } for question in page.get_questions(reply)]
            self.page = page
            initialpage = page.index()
        else:
            initialpage = 0

        self.fields['page_id'] = forms.IntegerField(required=True, widget=forms.HiddenInput,
                                                    initial=initialpage)


# @revision.create_on_success
def save_question_response(response, reply, page=None, question=None, variable_name=None):
    """Saves response as an Answer, unique within this Reply.

    If a previous answer to the question has been given within this Reply then
    the previous answer will be updated with a new Revision.
    """

    if variable_name:
        try:
            question = Question.objects.get(variable_name=variable_name)
            field_class = question.field_class()
            answer, created = Answer.objects.get_or_create(
                question=question,
                page=page,
                reply=reply)
            answer = field_class.save_answer(response, answer)

        except Question.DoesNotExist:
            # e.g. page_id's
            answer, created = Answer.objects.get_or_create(
                other_variable_name=variable_name,
                reply=reply,
            )
            answer.answer = response

    if created:
        revision.comment = "New answers saved"
    else:
        revision.comment = "Existing answers changed"

    answer.save(force_save=True)  # force save because answer may be readonly if versioning off
                                  # but we know we just created this one here
    return answer
