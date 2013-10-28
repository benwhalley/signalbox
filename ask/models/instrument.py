import re
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models
from question import ChoiceSet, Choice, Question
from signalbox.utilities.linkedinline import admin_edit_url


class Instrument(models.Model):
    """Groupings of questions which may be reused within questionnaires."""

    # objects = InstrumentManager()

    name = models.CharField(max_length=255, unique=True)
    citation = models.TextField(blank=True, null=True)
    usage_information = models.TextField(blank=True, null=True,
                                         help_text="""e.g. details of subscales, scoring information.""")


    def dump_json(self):
        """Export everything needed for this Instrument to a json fixture.

        Uses natural keys and resents numeric pk value to null, to ensure
        that deserialisation doesn't clash when imported into another db.
        """
        questions = self.question_set.all()
        question_in_instruments = Question.objects.filter(
            instrument=self)
        choicesets = ChoiceSet.objects.filter(
            id__in=set([i.choiceset.id for i in questions if i.choiceset]))
        choices = Choice.objects.filter(choiceset__in=choicesets)

        json = serializers.serialize('json',
                                     [self] + list(choicesets) + list(
                                     questions) + list(
                                         choices) + list(
                                             question_in_instruments),
                                     use_natural_keys=True,
                                     indent=2)

        json = re.sub(r'"pk": \d+,', r'"pk": null,', json)
        return json

    def used_in_askers(self):
        pass
        # return InstrumentInAskPage.objects.filter(instrument=self)

    def clean(self):
        """Limit questions to 1000 because of within-page numbering logic."""

        super(Instrument, self).clean()
        if self.pk and self.question_set.all().count() > 1000:
            raise ValidationError("More than 1000 questions not allowed.")

    class Meta:
        ordering = ['name']
        unique_together = ['name']
        app_label = 'ask'

    def admin_edit_url(self):
        return admin_edit_url(self)

    def __unicode__(self):
        return self.name or "Unnamed Instrument"


def addprefix(prefix, q):
    """Function to add a prefix to a Question's variable_name"""
    q.question.variable_name = prefix + q.question.variable_name
    return q


# class InstrumentInAskPage(models.Model):
#     """Link model to store references to Instruments in AskPages."""

#     instrument = models.ForeignKey('Instrument')

#     order = models.DecimalField(default=0, max_digits=4, decimal_places=1, verbose_name="Page order", help_text="""Place within the
#         page to display this instrument (includes individual questions above)""")

#     variable_prefix = models.CharField(max_length=6, blank=True, null=True)

#     page = models.ForeignKey('AskPage')

#     showif = models.ForeignKey('ask.ShowIf', null=True, blank=True,
#                                help_text="""Conditionally hide or show this Question based on these rules""",
#                                verbose_name="""Show the question if""")

#     allow_not_applicable = models.BooleanField(default=False)

#     require_all = models.BooleanField(default=False, help_text="""Will ensure that all questions
#         within the Instrument are required when the participant completes this questionnaire.""",
#                                       verbose_name="""Make all questions required""")

#     def showme(self, reply):
#         """Return a boolean indicating whether the question should be hidden."""

#         if self.showif:
#             return self.showif.evaluate(reply)
#         return True

#     def all_questions(self):
#         qlist = list(Question.objects.select_related(
#         ).filter(instrument=self.instrument))
#         prefix = self.variable_prefix
#         if prefix:
#             qlist = [addprefix(prefix, i) for i in qlist]

#         return qlist

#     def admin_edit_url(self):
#         return admin_edit_url(self, indirect_pk_field='instrument')

#     class Meta:
#         app_label = 'ask'
#         verbose_name_plural = "Instruments in the page"
#         ordering = ['instrument__name']
