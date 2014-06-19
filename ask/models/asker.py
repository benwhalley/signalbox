# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime
from functools import partial
import functools
import itertools
import json
import re

from ask.models import Choice
from ask.yamlextras import yaml, MyDumper
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import model_to_dict
from page import AskPage
from question import Question
from signalbox.utilities.djangobits import supergetattr, flatten, dict_map
from signalbox.utilities.linkedinline import admin_edit_url
from yamlfield.fields import YAMLField
from twiliobox.settings import IVR_SYSTEM_MESSAGES
from signalbox.custom_contracts import *


class AskerManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Asker(models.Model):

    objects = AskerManager()

    def natural_key(self):
        return (self.slug, )

    name = models.CharField(max_length=255, null=True)

    slug = models.SlugField(max_length=128, help_text="""To use in URLs etc""",
        unique=True, verbose_name="""Reference code""")

    success_message = models.TextField(default="Questionnaire complete.",
        help_text="""Message which appears in banner on users screen on completion of the  questionnaire.""")

    redirect_url = models.CharField(max_length=128, default="/profile/",
        help_text=""""URL to redirect to when Questionnaire is complete.""")

    show_progress = models.BooleanField(default=False, help_text="""Show a
            progress field in the header of each page.""")

    finish_on_last_page = models.BooleanField(default=False, help_text="""Mark the reply as complete
        when the user gets to the last page. NOTE this implies there should be not questions
        requiring input on the last page, or these values will never be saved.""")

    step_navigation = models.BooleanField(default=True, help_text="""Allow navigation
        to steps.""")

    steps_are_sequential = models.BooleanField(default=True, help_text="""Each page
        in the questionnaire must be completed before the next; if unchecked
        then respondents can skip around within the questionnaire and complete
        the pages 'out of order'.""")

    hide_menu = models.BooleanField(default=True)

    system_audio = YAMLField(blank=True, help_text="""A mapping of slugs to text strings or
        urls which store audio files, for the system to play on errors etc. during IVR calls""")

    def get_phrase(self, key):
        if self.system_audio:
            return self.system_audio.get(key, IVR_SYSTEM_MESSAGES.get(key))
        else:
            return IVR_SYSTEM_MESSAGES.get(key, None)

    def used_in_studies(self):
        from signalbox.models import Study
        return Study.objects.filter(studycondition__scripts__asker=self)

    def used_in_scripts(self):
        from signalbox.models import Script
        return Script.objects.filter(asker=self)

    def used_in_study_conditions(self):
        """Return a queryset of the StudyConditions in which this Asker appears."""
        from signalbox.models import StudyCondition
        scripts = self.used_in_scripts()
        conds = set(StudyCondition.objects.filter(scripts__in=scripts))
        return conds

    def approximate_time_to_complete(self):
        """Returns the approximate number of minutes the asker will take to complete.
        Rounded to the nearest 5 minutes (with a minumum of 5 minutes)."""

        baseround = lambda x, base=5: int(base * round(float(x) / base))
        n_questions = Question.objects.filter(page__in=self.askpage_set.all()).count()
        mins = (n_questions * .5) * .9
        return max([5, baseround(mins, 5)])

    def scoresheets(self):
        return itertools.chain(*[i.scoresheets() for i in self.askpage_set.all()])

    def summary_scores(self, reply):
        answers = reply.answer_set.all()
        return {i.name: i.compute(answers) for i in self.scoresheets()}

    @contract
    def questions(self, reply=None):
        """All questions, filtered by previous answers if a reply is passed in, see methods on Page.
        :rtype: list
        """

        questionsbypage = map(lambda i: i.get_questions(reply=reply), self.askpage_set.all())

        for i, pagelist in enumerate(questionsbypage):
            for q in pagelist:
                q.on_page = i

        questions = list(itertools.chain(*questionsbypage))
        return questions

    def first_page(self):
        return self.askpage_set.all()[0]

    def page_count(self):
        return self.askpage_set.all().count()

    def admin_edit_url(self):
            return admin_edit_url(self)

    def get_absolute_url(self):
        return reverse('preview_asker',
            kwargs={'asker_id': self.id, 'page_num': 0})

    def get_anonymous_url(self, request):
        return reverse('start_anonymous_survey',
                    kwargs={'asker_id': self.id})

    def json_export(self):
        """Export Asker and related objects as json.

        Export everything needed to recreate this questionnaire on
        another signalbox instance (or 3rd party system) with the
        exception of question assets."""

        _asdict = lambda object, fields: {i: unicode(supergetattr(object, i)) for i in fields}

        pages = self.askpage_set.all()
        questionlists = [i.get_questions() for i in pages]
        questions = list(itertools.chain(*questionlists))

        choicesets = set([i.choiceset for i in questions if i.choiceset])
        choices = Choice.objects.filter(choiceset__in=choicesets)

        QUESTION_FIELDS = ('natural_key', 'variable_name', 'order', 'required',
                           'help_text', 'text', 'choiceset.pk', 'q_type', 'showif')
        CHOICESET_FIELDS = ('natural_key', 'name')
        CHOICE_FIELDS = ('choiceset.natural_key', 'is_default_value', 'order',
                         'label', 'score')

        qdicts = [_asdict(i, QUESTION_FIELDS) for i in questions]
        # give a consistent ordering to everything
        [d.update({'order': i}) for i, d in enumerate(qdicts)]

        output = {
            'meta': {'name': self.slug,
                     'show_progress': self.show_progress,
                     'generated': str(datetime.now()),
                     },
            'questions': qdicts,
            'choicesets': [_asdict(i, CHOICESET_FIELDS) for i in choicesets],
            'choices': [_asdict(i, CHOICE_FIELDS) for i in choices],
            'scoresheets': [i.as_simplified_dict() for i in self.scoresheets()]
        }

        jsonstring = json.dumps(output, indent=4)

        return "{}".format(jsonstring)

    @contract
    def as_markdown(self):
        """A helper to convert an asker and associated models to markdown format.
        :rtype: string
        """

        _fields = "slug name steps_are_sequential redirect_url finish_on_last_page \
            show_progress success_message step_navigation system_audio".split()

        metayaml = yaml.safe_dump({i: getattr(self, i) for i in _fields},
            default_flow_style=False)

        _pages_questions = [
            (i.as_markdown(), [j.as_markdown() for j in i.get_questions()])
            for i in self.askpage_set.all()
        ]
        qstrings = "\n\n".join(flatten(flatten(_pages_questions)))

        return "---\n" + metayaml + "---\n\n" + qstrings

    class Meta:
        permissions = (
            ("can_preview", "Can preview surveys"),
        )
        verbose_name = "Questionnaire"
        app_label = "ask"
        ordering = ['name']

    def save(self, *args, **kwargs):
        # set defaults for system_audio if none exist
        if self.system_audio:
            if isinstance(self.system_audio, dict):
                IVR_SYSTEM_MESSAGES.update(self.system_audio)
            self.system_audio = IVR_SYSTEM_MESSAGES

        super(Asker, self).save(*args, **kwargs)

    def __unicode__(self):
        return "{}".format(self.name or self.slug)
