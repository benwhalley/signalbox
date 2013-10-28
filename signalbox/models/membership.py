import itertools
from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

from datetime import datetime
from signalbox.utils import proportion
from signalbox.utilities.linkedinline import admin_edit_url
from observation import Observation
from answer import Answer


class MembershipManager(models.Manager):

    def authorised(self, user):
        """Provide per-user access for Memberships.

        No-op at present."""

        qs = super(MembershipManager, self).select_related()

        return qs


class Membership(models.Model):
    """Users join Studies which is recorded in a Membership object. """


    objects = MembershipManager()

    active = models.BooleanField(default=True,
        help_text="""If deselected, Observations no longer be sent for Membership.""",
        db_index=True)

    user = models.ForeignKey(User)

    study = models.ForeignKey('Study',)

    relates_to = models.ForeignKey('Membership', blank=True, null=True,
        verbose_name="Linked patient",
        related_name="membership_relates_to",
        help_text="""Sometimes a researcher may themselves become a subject in a study (for
        example to provide ratings of different patients progress). In this instance they may
        be added to the study multiple times, with the relates_to field set to another User,
        for which they are providing data.""")

    condition = models.ForeignKey('StudyCondition', null=True, blank=True,
        help_text="""Choose a Study/Condition for this user. To use Randomisation you must
        save the Membership first, then randomise to a condition using the tools menu (or
        if set, the study may auto-randomise the participant).""")

    date_joined = models.DateField(auto_now_add=True)

    date_randomised = models.DateField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if self.condition:
            self.study = self.condition.study
        super(Membership, self).save(*args, **kwargs)

    def is_current(self):
        """Return True if the user has outstanding observations within a study."""
        obs = self.observation_set.all()
        return bool([o.status != 1 for o in obs]) and self.active


    def observations(self):
        """Return the observations for this Membership.
        """
        obs = self.observation_set.select_related()
        return obs

    def incomplete_observations(self):
        return self.observations().exclude(status=1)

    def has_observation_expiring_today(self):
        return sum([i.expires_today for i in self.observations()])

    # helper functions to calculate obs of various types
    outcomes = lambda self: self.observations(threshold=50)
    outcomes_due = lambda self:  [i for i in self.outcomes() if i.due < datetime.now()]
    outcomes_complete = lambda self: [i for i in self.outcomes() if i.status == 1]
    outcomes_due_complete = lambda self: [i for i in self.outcomes_due() if i.status == 1]
    prop_outcomes_complete = lambda self: proportion(
        len(self.outcomes_complete()), len(self.outcomes()))
    prop_outcomes_due_complete = lambda self: proportion(
        len(self.outcomes_due_complete()), len(self.outcomes_due()))


    def randomised(self):
        return bool(self.condition)


    def make_ad_hoc_observation(self):
        """Make an ad hoc Observation, save it, and return it."""

        rightnow = datetime.now()
        newobs = Observation(   status=-1,
                                dyad=self,
                                due=rightnow,
                                due_original=rightnow,
                                label="Ad hoc observation")
        newobs.save()
        return newobs


    def add_observations(self):
        """Creates and saves Observations -> [Observation]."""

        if not self.condition:
            return []

        observations = []
        observations = itertools.chain(*
            [s.make_observations(membership=self) for s in self.condition.scripts.all()]
        )

        self.save()

        return observations


    def questions_answered(self):
        return Answer.objects.filter(reply__observation__in\
            =self.observation_set.all()).count()

    def admin_edit_url(self):
            return admin_edit_url(self)


    class Meta:
        permissions = (("can_add_observations", "Can generate observations for a membership"),
                       ("can_randomise_user", "Can randomise a user"),)
        verbose_name = "Study membership"
        app_label = 'signalbox'
        ordering = ['-date_randomised']


    def __unicode__(self):
        string = getattr(self, 'study', "None")
        return '%s, member of %s' % (self.user.username, string)
