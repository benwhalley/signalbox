from datetime import timedelta
from datetime import datetime
from django import template

register = template.Library()

from signalbox import models


@register.tag(name="get_observations")
def get_observations(parser, token):
    tag_name, study_id, period, obtype = token.split_contents()
    return ObservationsCount(study_id, period[1:-1], obtype[1:-1])

class ObservationsCount(template.Node):
    def __init__(self, study_id, period, obtype):
        self.study_id = template.Variable(study_id)

        self.period = None
        if period == "current":
            self.period = [datetime.today()-timedelta(days=7), datetime.today()+timedelta(days=7)]

        if period == "lastmonth":
            self.period = [datetime.today()-timedelta(days=30), datetime.today()]

        self.obtype = obtype

    def render(self, context):
        observations = models.Observation.objects.filter(dyad__study__id=self.study_id.resolve(context))

        if self.period:
            observations = observations.filter(due__range=self.period)

        if self.obtype == "incomplete":
            observations = observations.filter(status__lt=1)

        return observations.count()
