from __future__ import division

from django.db import models
from collections import defaultdict
from signalbox.settings import SCORESHEET_FUNCTION_NAMES, SCORESHEET_FUNCTION_LOOKUP

def float_or_none(string):
    """Try to turn a string into a float, but return None if this fails."""

    try:
        return float(string)
    except ValueError:
        return None


class ScoreSheet(models.Model):
    name = models.SlugField(blank=True, max_length=80, unique=True)
    description = models.TextField(blank=True)
    minimum_number_of_responses_required = models.IntegerField(null=True, blank=True)
    variables = models.ManyToManyField(
        'ask.Question', related_name="varsinscoresheet")
    function = models.CharField(max_length=200, choices=[(i, i) for i in SCORESHEET_FUNCTION_NAMES])

    def as_str_for_yaml(self):
        return "{}({})".format(self.function, " ".join([i.variable_name for i in self.variables.all()]))

    def as_simplified_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'variable_names': [i.variable_name for i in self.variables.all()],
            'function': self.function
        }

    def min_number_variables(self):
        return self.minimum_number_of_responses_required or self.variables.all().count()

    def score_function(self):
        return SCORESHEET_FUNCTION_LOOKUP[self.function]

    def compute(self, answers):
        """Returns a dictionary containing score, scoresheet and a message.

        Note by default all variables must have a corresponding answer in the Reply, but this can
        be overridden by the minimum_number_of_responses_required field on the ScoreSheet.
        """

        variable_names = [q.variable_name for q in self.variables.all()]
        answers = [a for a in answers if a.question and a.answer]
        answers_to_use = [a for a in answers if a.question.variable_name in variable_names]

        try:
            scores = [float_or_none(a.mapped_score()) for a in answers_to_use]
            scores = [a for a in scores if a != None]

            if len(scores) < self.min_number_variables():
                return {'scoresheet':self, 'score':None, 'message': "Only %s variables submitted" % len(scores)}
            else:
                return {'scoresheet':self, 'score':self.score_function()(scores), 'message': ""}

        except Exception as e:
            return {'scoresheet':self, 'score':None, 'message': str(e)}


    def __unicode__(self):
        return "%s (%s)" % (self.name, self.function)

    class Meta:
        app_label = "signalbox"
