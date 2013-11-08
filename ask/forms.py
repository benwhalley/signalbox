"""Forms for the Ask application"""
import os
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from reversion import revision
from ask.models import Question, ChoiceSet, Instrument, AskPage
from signalbox.models import Answer
from django.conf import settings
import floppyforms as forms
from signalbox.models.listeners import user_input_received
from ask.models.fields import FIELD_NAMES
from django.utils.encoding import smart_unicode
import ask.validators as valid
from ask.utils import statify
from twilio import twiml


class PageForm(forms.Form):
    """Dynamically generated form, from the list of questions in **kwargs."""

    def save(self, *args, **kwargs):

        reply = kwargs.pop('reply')
        page = kwargs.pop('page')
        for key, val in self.cleaned_data.iteritems():
            save_question_response(val, reply, page, variable_name=key)
        user_input_received.send(self, reply=reply)
        return True

    def __init__(self, *args, **kwargs):
        """Overridden to dynamically create form."""

        reply = kwargs.pop('reply')
        page = kwargs.pop('page')
        request = kwargs.pop('request')

        if page:
            self.questions_to_show = page.questions_to_show(reply)
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
            self.conditional_questions = [{'question': question, 'showif': question.showif}
                for question in page.questions_to_show()]
            self.page = page
            initialpage = page.index()
        else:
            initialpage = 0

        self.fields['page_id'] = forms.IntegerField(required=True,
            widget=forms.HiddenInput, initial=initialpage)


@revision.create_on_success
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

    answer.save()
    return answer


class BulkAddQuestionsForm(forms.Form):

    add_to_instrument = forms.ModelChoiceField(required=False, queryset=Instrument.objects.all(),
        help_text="""Leave blank to create a new instrument""")

    questions = forms.CharField(required=True,
        widget=forms.widgets.Textarea(attrs={'cols': '80'}),
        help_text="Add questions, one per line")
    variable_names = forms.CharField(required=False,
        widget=forms.widgets.Textarea(attrs={'cols': '20', 'class': 'varnames'}),
        help_text="""Variable names can use characters a-Z, 0-9 and underscore (_), and must be
        unique within the system.""")
    q_type = forms.ChoiceField(required=True, initial="likert", choices=[(i, i.upper()) for i in FIELD_NAMES])
    choiceset = forms.ModelChoiceField(required=False, queryset=ChoiceSet.objects.all())

    def clean(self):
        cleaned_data = self.cleaned_data

        names = cleaned_data.get('variable_names', "")
        questions = cleaned_data['questions']

        cleanupf = lambda x: smart_unicode(x, encoding='utf-8', strings_only=False, errors='strict')
        names = filter(bool, map(cleanupf, names.split("\r\n")))
        questions = filter(bool, map(cleanupf, questions.split("\r\n")))

        hasnaughtychars = lambda x: bool(sum([i in x for i in "-*!"]))

        if len(names) != len(questions):
            raise forms.ValidationError("Number of questions and variable names doesn't match.")

        # do some more checks... these functions can raise ValidationErrors
        map(valid.illegal_characters, names)
        map(valid.first_char_is_alpha, names)
        map(valid.is_lower, names)
        map(valid.less_than_n_chars, names)

        cleaned_data.update(
            {'variable_names': names, 'questions': questions,}
        )

        return cleaned_data
