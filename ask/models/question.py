# -*- coding: utf-8 -*-
import json
from pyparsing import *
from ask.models.fields import FIELD_NAMES
import ask.validators as valid
from ask.yamlextras import yaml
import ast
from django import http
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.loading import get_model
from django.forms.models import model_to_dict
from django.template import Context, Template
from django.template.loader import get_template

import fields
from jsonfield import JSONField
import markdown

from signalbox.exceptions import DataProtectionException
from signalbox.utilities.djangobits import supergetattr, flatten, safe_help, int_or_string
from signalbox.utilities.linkedinline import admin_edit_url
from signalbox.custom_contracts import *
from yamlfield.fields import YAMLField
from parse_conditional import parse_conditional


truncatelabel = lambda x, y: (x[:int(y) / 2] + '...' + x[- int(y) / 2:]) if len(x) > y else x

DEFAULTYAMLCHOICESET = """
1:
  label: 'One'
  score: 1
2:
  is_default_value: true
  label: 'Two'
  score: 2
3:
  label: 'More than two'
  score: 2
    """

ASSET_TEMPLATE_CHOICES = (
    ('image.html', 'image'),
    ('movie.html', 'movie'),
    ('audio.html', 'audio'),
)


class QuestionAsset(models.Model):

    question = models.ForeignKey('ask.Question')
    slug = models.SlugField(help_text="""A name to refer to this asset
        with in the question_text field. To display an image or media
        player within the question, include the text {{SLUG}} in the
        question_text field of the question.""")
    asset = models.FileField(upload_to="questionassets", blank=True, null=True,
        help_text="""Can be an image (.jpg, .png, or .gif), audio file (.m4a, .mp4, or .mp3) or
        movie (.mp4 only) for display as part of the question text.""")
    template = models.CharField(max_length=255,
        choices=ASSET_TEMPLATE_CHOICES, )

    def render(self):
        templ = get_template("questionasset/" + self.template)
        context = {'object': self}
        return templ.render(Context(context))

    def __unicode__(self):
        return self.render()

    class Meta:
        app_label = 'ask'


class QuestionManager(models.Manager):
    def get_by_natural_key(self, variable_name):
        return self.get(variable_name=variable_name)


class Question(models.Model):
    """Question objects; e.g. mutliple choice, text, etc."""

    def check_if_protected(self):
        nonpreviewanswercount = self.answer_set.exclude(
            reply__entry_method="preview").count()
        # if we have non-preview answers, don't allow the question to be edited
        if nonpreviewanswercount:
            raise DataProtectionException("""This question (%s) already has
                answers attached to it and can't be modified.""" % self, )

    def delete(self, *args, **kwargs):
        # we delete preview answers to this questions to avoid ProtectedErrors
        # when deleting questions through the admin or in the yaml interface
        self.answer_set.filter(reply__entry_method="preview").delete()
        self.check_if_protected()
        super(Question, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.check_if_protected()
        super(Question, self).save(*args, **kwargs)

    def index(self):
        return self.page.asker.questions().index(self)

    def dict_for_yaml(self):
        d = {
            "text": self.text,
            "q_type": self.q_type,
            "choiceset": supergetattr(self, "choiceset.name", None),
            "required": self.required,
        }
        return {self.variable_name: {k: v for k, v in d.items() if v}}

    page = models.ForeignKey('ask.AskPage', null=True, blank=True)
    scoresheet = models.ForeignKey('signalbox.ScoreSheet', blank=True, null=True)

    objects = QuestionManager()

    def natural_key(self):
        return (self.variable_name, )
    natural_key.dependencies = ['ask.choiceset', 'ask.AskPage']

    order = models.IntegerField(default=-1, verbose_name="Page order",
        help_text="""The order in which items will apear in the page.""")

    allow_not_applicable = models.BooleanField(default=False)

    required = models.BooleanField(default=False)

    @contract
    def show_conditional(self, mapping_of_answers):
        """
        Use pyparsing to match an 'if' keyval on questions.
        :type mapping_of_answers: dict
        :rtype: bool
        """

        try:
            condition = self.extra_attrs.get('if', None)
        except AttributeError:
            condition = None

        show = parse_conditional(condition, mapping_of_answers)
        return show

    text = models.TextField(blank=True, null=True,
        help_text=safe_help(settings.QUESTION_TEXT_HELP_TEXT)
        )

    variable_name = models.SlugField(default="", max_length=32, unique=True,
        validators=[valid.first_char_is_alpha, valid.illegal_characters,
            valid.is_lower], help_text="""Variable names can use characters a-Z,
            0-9 and underscore (_), and must be unique within the system.""")

    choiceset = models.ForeignKey('ask.ChoiceSet', null=True, blank=True)

    help_text = models.TextField(blank=True, null=True)
    javascript = models.TextField(blank=True, null=True)
    

    @contract
    def show_as_image_data_url(self):
        """Say whether the answer is a stored data url for an image.
        :rtype: bool
        """
        if self.q_type == "webcam":
            return True
        return False

    @contract
    def display_text(self, reply=None, request=None):
        """
        :type reply: is_reply|None
        :type request: c|None

        :return: The html formatted string displaying the question
        :rtype: string
        """


        templ_header = r"""{% load humanize %}"""  # include these templatetags in render context
        templ = Template(templ_header + self.text)
        context = {
            'reply': reply,
            'user': supergetattr(reply, 'observation.dyad.user', default=None),
            'page': self.page,
            'scores': {},
            'answers': {},
            'answers_label': {}
        }

        fc = self.field_class()
        if reply and reply.asker and fc.compute_scores:
            context['scores'] = self.page.summary_scores(reply)
            # put actual values into main namespace too
            context.update({k: v.get('score', None) for k, v in context['scores'].items()})

        if fc.allow_showing_answers and reply:
            context['answers'] = {i.variable_name(): int_or_string(i.answer) for i in reply.answer_set.all()}

        for i in self.questionasset_set.all():
            context[i.slug] = unicode(i)

        return markdown.markdown(templ.render(Context(context)))

    q_type = models.CharField(choices=[(i, i) for i in FIELD_NAMES],
        blank=False, max_length=100, default="instruction")

    def field_class(self):
        """Return the relevant form field Class"""
        return getattr(fields, fields.class_name(self.q_type))

    def preview_html(self):
        """Return a form with a single question which can be used to preview questions -> PageForm"""
        from ask.forms import PageForm  # yuck but circular imports
        request = http.HttpRequest()
        form = PageForm(None, None,
                        page=None, questions=[self], reply=None, request=request)
        return form

    def label_variable(self):
        return self.field_class().label_variable(self)

    def set_format(self):
        return self.field_class().set_format(self)

    def label_choices(self):
        return self.field_class().label_choices(self)

    extra_attrs = YAMLField(blank=True, help_text="""A YAML representation of a python dictionary of
        attributes which, when deserialised, is passed to the form widget when the questionnaire is
        rendered. See django-floppyforms docs for options.""")

    def extra_attrs_as_yaml(self):
        return yaml.dump(self.extra_attrs, default_flow_style=False)

    def voice_function(self):
        """Returns the function to render instructions for external telephony API."""

        return self.field_class().voice_function

    def choices_as_json(self):
        """Question -> String"""
        return self.choiceset and self.choiceset.values_as_json() or ""

    @contract
    def choices(self):
        """
        :rtype: None|list(tuple)
        """

        return (self.choiceset and self.choiceset.choice_tuples()) or None

    def response_possible(self):
        """:: Question -> Bool
        Indicates whether a user response is possible for this Question"""
        return self.field_class().response_possible

    @contract
    def check_telephone_keypad_answer(self, raw_response_as_string):
        """Check a user response to see if it is allowed by the question.
        :type raw_response_as_string: string
        :rtype: bool
        """

        if not self.response_possible():
            # if no response expected we don't care what they pressed
            return True

        if self.choiceset:
            try:
                return bool(int(raw_response_as_string) in self.choiceset.allowed_responses())
            except ValueError:
                # can't case string to an int, so not allowed
                return False

        # If we have no choiceset specified then anything is allowed
        return True

    @contract
    def previous_answer(self, reply):
        """
        Return the an earlier answer if one exists for this reply.
        :rtype: string|None
        """
        from signalbox.models import Answer  # yuck, but otherwise circular import hell

        if not self.response_possible() or not reply:
            return None
        try:
            return reply.answer_set.get(question=self, page=self.page).answer
        except Answer.DoesNotExist:
            return ""

    def __unicode__(self):
        return truncatelabel(self.variable_name, 26)

    MARKDOWN_FORMAT = u"""~~~{{{variable_name} {classes} {keyvals} }}\n{text}\n{details}\n~~~"""

    def as_markdown(self):

        iden = "#" + self.variable_name
        if self.extra_attrs:
            classes = self.extra_attrs.pop('classes', {})
            classesstring = " ".join([".{}".format(k) for k, v in classes.items() if v])
        else:
            classesstring = ".{}".format(self.q_type)

        keyvals = self.extra_attrs or {}
        keyvalsstring = " ".join(["""{}="{}" """.format(k, v) for k, v in keyvals.items()])

        detailsstring = ""
        if self.choiceset:
            detailsstring = u">>>\n" + self.choiceset.as_markdown()
        elif self.scoresheet:
            detailsstring = u">>>\n" + self.scoresheet.as_markdown()

        return self.MARKDOWN_FORMAT.format(**{
            'variable_name': iden,
            'classes': classesstring,
            'keyvals': keyvalsstring,
            'text': self.text,
            'details': detailsstring
            }
        )

    def clean(self, *args, **kwargs):

        self.variable_name = self.variable_name.replace("-", "_")
        super(Question, self).clean(*args, **kwargs)

    def clean_fields(self, *args, **kwargs):
        """Do some extra validation related to form fields used for the question."""

        super(Question, self).clean_fields(*args, **kwargs)

        if not self.q_type:
            return False

        fieldclass = self.field_class()

        errors = {}

        if self.order is -1:
            self.order = 1 + self.page.question_set.all().count()

        if self.q_type in "slider" and not self.widget_kwargs:
            errors['widget_kwargs'] = ["""No default settings for slider added
            (need min, max, value). E.g. {"value":50,"min":0,"max":100}"""]

        if "range-slider" in self.q_type and not self.widget_kwargs:
            errors['widget_kwargs'] = ["""Default settings for slider added
            (need values [a,b], min, max). E.g. {"values":[40,60],"min":0,"max":100}.
            Optional extra attributes: {"units":"%" } """]

        if (not fieldclass.has_choices) and self.choiceset:
            errors['choiceset'] = ["You don't need a choiceset for this type of question."]

        if fieldclass.has_choices and (not self.choiceset):
            errors['choiceset'] = ["You need a choiceset for this type of question."]

        if self.required and (not fieldclass.response_possible):
            errors['required'] = ["This type of question (%s) doesn't allow a response." % (self.q_type,)]

        if errors:
            raise ValidationError(errors)

    def admin_edit_url(self):
        return admin_edit_url(self)

    class Meta:
        app_label = 'ask'
        ordering = ['order']


class ChoiceManager(models.Manager):
    def get_by_natural_key(self, choiceset, label, score):
        return self.get(choiceset=choiceset, label=label, score=score)


class Choice(models.Model):
    """A possible option to choose in response to a Question."""

    objects = ChoiceManager()

    def natural_key(self):
        return (self.choiceset, self.label, self.score)
    natural_key.dependencies = ['ask.choiceset']

    choiceset = models.ForeignKey('ask.ChoiceSet', blank=True, null=True)

    is_default_value = models.BooleanField(default=False, db_index=True,
        help_text="""Indicates whether the value will be checked by default.""")

    order = models.IntegerField(db_index=True, help_text="""Order in which the choices are displayed.""")

    label = models.CharField(u"Label", max_length=200, blank=True, null=True)

    score = models.IntegerField(help_text="This is the value saved in the DB")

    mapped_score = models.IntegerField(blank=True, null=True,
        help_text="""The value to be used when computing scoresheets. Does not affect what is stored or exported.""")

    def __unicode__(self):
        return u'%s (%s)' % (self.label, self.score)

    class Meta:
        app_label = 'ask'
        ordering = ['order']
        unique_together = (('choiceset', 'score'),)


class ChoiceSetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class ChoiceSet(models.Model):
    """The set of options attached to Questions."""

    objects = ChoiceSetManager()
    name = models.SlugField(max_length=64, unique=True)
    yaml = YAMLField(blank=True, validators=[valid.checkyamlchoiceset], default=DEFAULTYAMLCHOICESET)

    def natural_key(self):
        return (self.name, )

    def __unicode__(self):
        return self.natural_key()

    def dict_for_yaml(self):
        sd = {i.order:
            {'score': i.score, 'label': i.label, 'is_default_value': i.is_default_value}
            for i in self.get_choices()}
        # comprehension to filter out null values to make things clearer to edit by hand
        sd = {k: {a: b for a, b in v.items() if b is not None} for k, v in sd.items()}
        return {self.name: sd}

    @contract
    def default_value(self):
        """
        :returns: The default value of the choiceset
        :rtype: int|None
        """
        choices = filter(lambda x: x.is_default_value, self.get_choices())
        if choices:
            return int(getattr(choices[0], 'is_default_value'))

    def values_as_json(self):
        choices = dict([(unicode(i.score), unicode(i.label)) for i in self.get_choices()])
        return json.dumps(choices, indent=4, sort_keys=True)

    @contract
    def choice_tuples(self):
        """
        :returns: A list of tuples containing scores and labels.
        :rtype: list(tuple(int, string))
        """
        return [(int(i.score), i.label) for i in self.get_choices()]

    MARKDOWN_FORMAT = u"""{isdefault}{score}{mapped_score}={label} """

    def as_markdown(self):
        if not self.yaml:
            self.yaml = {i: d for i, d in enumerate(
                [{'score': x.score, 'isdefault': x.is_default_value, 'label': x.label} for x in self.get_choices()])}

        def _formatmappedscore(c):
            score = c['score']
            mapped_score = c.get('mapped_score', score)
            return mapped_score != score and "[{}]".format(mapped_score) or ""

        return "\n".join([
            self.MARKDOWN_FORMAT.format(**{
                'isdefault': c.get('isdefault', "") and "*" or "",
                'score': c['score'],
                'mapped_score': _formatmappedscore(c),
                'label': c['label'],
            }
            )
            for i, c in self.yaml.items()])

    # synonym in case we want to change display
    choices_as_string = lambda self: self.as_markdown()

    def get_choices(self):
        """
        "returns: A sorted list of Choice objects
        :rtype: list(a)

        # this is transitional... choicesets are now specified as Yaml rather than via
        # db-saved Choice objects, but we recreate them by hand to avoid editing code elsewhere
        """

        if self.yaml:
            try:
                return sorted(
                    [Choice(choiceset=self, score=choice.get('score'),
                    mapped_score=choice.get('mapped_score', choice.get('score')),
                    is_default_value=choice.get('isdefault', False), label=choice.get('label', ''), order=i)
                    for i, choice in self.yaml.items()],
                    key=lambda x: x.order)
            except:
                return []
        else:
            # or if no yaml set, do it the old way
            cset = list(Choice.objects.filter(choiceset=self).order_by("order"))
            return cset

    @contract
    def allowed_responses(self):
        """
        :returns: A list of valid options, e.g. used to validate user input
        :rtype: list(int)
        """
        return [int(i.score) for i in self.get_choices()]

    def __unicode__(self):
        return u'%s' % (self.name, )

    class Meta:
        app_label = 'ask'
        ordering = ["name"]


class ShowIf(models.Model):
    """Defines a pattern of responses which can:
        - determine if a question is shown/hidden
        - trigger responsive mode data collection
        - trigger an alert
    """

    class Meta:
        app_label = 'ask'

    previous_question = models.ForeignKey('ask.Question', blank=True, null=True,
        related_name="previous_question",
        help_text='''For previous values, enter the name of the question which
        will already have been answered in this survey (technically, within this Reply)''')

    summary_score = models.ForeignKey('signalbox.ScoreSheet', blank=True, null=True,
        help_text="""A summary score to be calculated based on answer already entered in the current
        Reply.""")

    values = models.CharField(max_length=255, blank=True, null=True,
        help_text='''CASE INSENSITIVE values to match, comma separated. The question is shown if
        any value matches''')

    more_than = models.IntegerField(blank=True, null=True, help_text="""Previous question response
        or summary score must be more than this value.""")

    less_than = models.IntegerField(blank=True, null=True, help_text="""Previous question response
        or summary score must be less than this value.""")

    @contract
    def evaluate(self, reply):
        """Check whether a suitable previous answer exists and return Boolean.

        :rtype: bool
        """

        if self.summary_score:
            vals_to_be_tested = set([self.summary_score.compute(reply.answer_set.all())['score']])

        if self.previous_question:
            previous_answer = self.previous_question.previous_answer(reply)
            previous_answer = previous_answer and ast.literal_eval(previous_answer)
            flatlistofprevanswers = flatten([previous_answer])
            vals_to_be_tested = set(flatlistofprevanswers)

        if self.values:
            valid_value_set = set(self.valid_values())
            vals_to_be_tested = map(str, vals_to_be_tested)
            return bool(not valid_value_set.isdisjoint(vals_to_be_tested))

        if (self.more_than or self.less_than):
            inrange = lambda x: x > self.more_than and x < self.less_than
            return False not in map(inrange, vals_to_be_tested)

    def lowest(self):
        """Return a number that the user's previous response should be higher than"""
        return self.more_than or float("-inf")

    def highest(self):
        """Return a number that the user's previous response should be lower than"""
        return self.less_than or float("inf")

    def valid_values(self):
        """Return a Set of valid lowercased values to match against."""
        vals = self.values.split(",")
        return set([v.strip().lower() for v in vals])

    def clean(self):
        super(ShowIf, self).clean()

        if self.values and supergetattr(self, 'previous_question.choices', None):
            possibles = set(self.previous_question.choiceset.allowed_responses())
            vals = set(filter(bool, map(valid.is_int, self.values.split(","))))
            if not vals.issubset(possibles):
                raise ValidationError("""Valid choices for the selected question are: %s""" % (
                    "; ".join(map(str, possibles)), ))

        if self.previous_question and self.summary_score:
            raise ValidationError("""You can hide/show this item based on a previous question value
            or a summary score, but not both.""")

        if self.values and (self.less_than or self.more_than):
            raise ValidationError("""You can either specify a range using the more_than and
            less_than fields, or exact values, but not both.""")

        if not self.values and not (self.less_than or self.more_than):
            raise ValidationError(
                """Please specify a list of values to match, or a range.""")

    def conditions_as_strings(self):
        conditions = []
        if self.values:
            conditions.append('in [{}]'.format(self.values))
        if self.less_than:
            conditions.append('< {}'.format(self.highest()))
        if self.more_than:
            conditions.append('> {}'.format(self.lowest()))
        return conditions

    def thing_to_be_tested(self):
        if self.previous_question:
            return self.previous_question.variable_name
        else:
            return self.summary_score.__unicode__()

    def as_json(self):
        return json.dumps(self.as_simplified_dict(), indent=2)

    def operator_as_string(self):
        workouttypeofshowif = tuple(map(bool,
            [
                self.less_than,
                self.more_than,
                self.values,
                bool(self.values and len(self.values.split(",")) > 1)
            ]
        ))

        mapping = {
            (True, False, False, False): "<{}".format(self.less_than),
            (False, True, False, False): ">{}".format(self.more_than),
            (False, False, True, False): "={}".format(self.values),
            (False, False, True, True): " in [{}]".format(self.values),
        }
        return mapping[workouttypeofshowif]

    def as_markdown(self):
        return "{}{}".format(self.previous_question.variable_name, self.operator_as_string())

    def as_simplified_dict(self):
        return {'previous_value_name': self.thing_to_be_tested(),
        'conditions': self.conditions_as_strings()}

    def __unicode__(self):
        return "%s %s" % (self.thing_to_be_tested(), self.conditions_as_strings())
