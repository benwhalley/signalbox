#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ask.models import Choice, Instrument
from datetime import datetime
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import models
from django.forms.models import model_to_dict
from functools import partial
from page import AskPage
from signalbox.utilities.djangobits import supergetattr, flatten, dict_map
from signalbox.utilities.linkedinline import admin_edit_url
import functools
import itertools
import json
import re
from ask.yamlextras import yaml, MyDumper
from collections import OrderedDict


def filtered_model_to_dict(instance, fields=None, exclude=None):
    fields = fields or []
    exclude = exclude or []

    d = model_to_dict(instance)

    if exclude:
        return {k: v for k, v in d.items() if k not in exclude}

    if not fields:
        fields = d.keys()

    return {k:v for k, v in d.items() if k in set(fields)}



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

    redirect_url = models.CharField(max_length=128, default="/accounts/profile/",
        help_text=""""URL to redirect to when Questionnaire is complete.""")

    show_progress = models.BooleanField(default=False, help_text="""Show a
            progress field in the header of each page.""")

    step_navigation = models.BooleanField(default=True, help_text="""Allow navigation
        to steps.""")

    steps_are_sequential = models.BooleanField(default=True, help_text="""Each page
        in the questionnaire must be completed before the next; if unchecked
        then respondents can skip around within the questionnaire and complete
        the pages 'out of order'.""")

    scoresheets = models.ManyToManyField(
        'signalbox.ScoreSheet', blank=True, null=True,
        help_text="""Attach ScoreSheet rules to obtain summary (sum or mean)
        scores of groups of answers for each Reply made to Observations within
        this study.""",
        verbose_name="""Summary scores to compute""")

    hide_menu = models.BooleanField(default=True)

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
        n_questions = len(self.questions())
        mins = (n_questions * .5) * .9
        return max([5, baseround(mins, 5)])

    def as_yaml(self):

        asker = filtered_model_to_dict(self, exclude="id scoresheets redirect_url hide_menu".split())

        questionsbypage = [{i.step_name: [q.dict_for_yaml() for q in i.get_questions()]} for i in self.askpage_set.all()]

        choicesets = {}
        [choicesets.update(i.choiceset.dict_for_yaml()) for i in self.questions() if i.choiceset]

        d = [{"asker":asker}] + questionsbypage + [{"choicesets":choicesets}]

        return yaml.dump_all(d, Dumper=MyDumper,
            allow_unicode=True,
            default_flow_style = False,
            width=80, indent=2
            ).replace("---", "---\n\n") #.replace("\n-", "\n\n-")


    def questions(self):
        questionsbypage = map(lambda i: i.get_questions(),  self.askpage_set.all())

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
            'scoresheets': [i.as_simplified_dict() for i in self.scoresheets.all()]
        }

        jsonstring = json.dumps(output, indent=4)

        return "{}".format(jsonstring)

    class Meta:
        permissions = (
            ("can_preview", "Can preview surveys"),
        )
        verbose_name = "Questionnaire"
        app_label = "ask"

    def __unicode__(self):
        return "{}".format(self.name or self.slug)
