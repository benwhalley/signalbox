from django.db import models
from signalbox.utilities.djangobits import render_string_with_context
from signalbox.models import Observation
from signalbox.exceptions import SignalBoxException


class ObservationCreator(models.Model):
    """A rule used to monitor Replies and conditionally make a new Observation.

    ObservationCreators automatically calculate a score based on each new reply
    which is added and, if this meets a specified criteria, can add additional
    Observations for a participant to complete.

    For example, an automated phone call might ask a participant 1 or 2 quick
    questions to see whether a rare event has occured (e.g. have they been
    involved in a car crash? If they answer 'Yes', then an ObservationCreator
    might be set such that an additional followup email is sent to gather more
    information on this event.

    ObservationCreator's are attached to Study objects, and refer to a ShowIf
    object and a Script. The script is executed if the ShowIf evaluates to True,
    using the current Reply.

    A listener is used to check incoming replies to see if they meet the
    criteria set out by ObservationCreator objects. See :func:`signalbox.models.
    listeners.create_observations_in_response_to_user_answers` for more details
    of this.

    """

    script = models.ForeignKey('signalbox.Script')
    showif = models.ForeignKey('ask.ShowIf')

    def make_new_observations(self, reply):
        """Returns a list of new (saved) observations created if Reply meets conditions."""

        membership = reply.observation.dyad

        if not membership:
            raise SignalBoxException("We can't add observations if no membership exists")

        if not self.showif.evaluate(reply):
            return []  # no new observations need creating

        times = self.script.datetimes()
        observations = [Observation(
            label=render_string_with_context(
                self.script.label, {'script': self.script, 'membership': membership}),
            due_original=time,
            dyad=reply.observation.dyad,
            created_by_script=self.script
        )
            for time in times]
        [i.save() for i in observations]

        [o.add_data(key="created", value="Observation created by script id: {} \
            ({}) in reply: {}".format(self.id, self, reply.token)) for o in observations]

        return observations

    class Meta:
        app_label = 'signalbox'

    def __unicode__(self):
        return "(%s) Script %s if %s" % (self.id, self.script, self.showif)
