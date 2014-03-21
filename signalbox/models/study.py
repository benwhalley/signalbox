# -*- coding: utf-8 -*-

from __future__ import division

from datetime import datetime, timedelta
import itertools

from ask.models import Question
from contracts import contract
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models.loading import get_model
from django.template import Context, loader
from signalbox.models import Reply, Answer
from signalbox.models.validators import is_24_hour, only_includes_allowed_fields
from signalbox.utils import incomplete, in_range
from statlib.stats import chisquare


User = settings.AUTH_USER_MODEL


class StudySite(models.Model):
    """Location (for multicenter studies) at which participants recruited."""

    name = models.CharField(max_length=500,
                            help_text="""e.g. 'Liverpool', 'London' """)

    class Meta:
        app_label = 'signalbox'

    def __unicode__(self):
        return self.name


class StudyManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Study(models.Model):
    """Details of a study (or substudy or a large trial)."""

    objects = StudyManager()

    def natural_key(self):
        return (self.slug, )

    auto_randomise = models.BooleanField(default=True,
                                         help_text="""If on, then users are automatically added to a study
            condition when a new membership is created.""")

    auto_add_observations = models.BooleanField(default=True,
            help_text="""If on, and auto_randomise is also on, then observations will
            be created when a membership is created. Has no effect if
            auto_randomise is off.""")

    visible = models.BooleanField(default=False,
        help_text="""Controls the display of the study on the /studies/ page.""", db_index=True)

    paused = models.BooleanField(default=False,
        help_text="""If True, pauses sending of signals. Observations missed
        will not be caught up later without manual intervention.""", db_index=True)

    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership', )

    slug = models.SlugField(help_text="""A short name
        used to refer to the study in URLs and other places.""")

    name = models.CharField(max_length=200)

    study_email = models.EmailField(blank=False,
                                    help_text="The return email address for all mailings/alerts.")

    twilio_number = models.ForeignKey('twiliobox.TwilioNumber', blank=True, null=True)

    ad_hoc_askers = models.ManyToManyField(
        'ask.Asker', blank=True, null=True,
        help_text="""Questionnaires which can be completed ad-hoc.""",
        verbose_name="Questionnaires available ad-hoc")

    ad_hoc_scripts = models.ManyToManyField(
        'signalbox.Script', blank=True, null=True,
        help_text="""Scripts which can be initiated by users on an ad-hoc basis.
        IMPORTANT. Scripts selected here will appear on the 'add extra data' tab
        of participants' profile pages, and will display the name of the study,
        and the name of the script along with the username of any related
        membership. BE SURE THESE DO NOT LEAK INFORMATION you would not which
        participants to see.""",
        verbose_name="""scripts allowed on an ad-hoc basis""")

    createifs = models.ManyToManyField(
        'signalbox.ObservationCreator', null=True, blank=True,
        help_text="""Rules by which new observations might be made in response
        to participant answers.""", verbose_name="""Rules to create new
        observations based on user responses""")

    blurb = models.TextField(blank=True, null=True, help_text="""Snippet of
        information displayed on the studies listing page.""")

    study_image = models.ImageField(blank=True, null=True,
                                    upload_to="study/images/")

    briefing = models.TextField(blank=True, null=True,
        help_text="""Key information displayed to participants before joining
        the study.""")

    consent_text = models.TextField(blank=True, null=True,
        help_text="""User must agree to this before entering study.""")

    welcome_text = models.TextField(blank=True, null=True,
        default="""Welcome to the study""",
        help_text="""Text user sees in a message box when they signup for the
        the study. Note his message is not needed if participants will be
        added to studies by the experimenter, rather than through the
        website.""")

    max_redial_attempts = models.IntegerField(default=3,
        help_text='''Only relevant for telephone calls: maximium
        number of times to try and complete the call. Default
        if nothing is specified is 3''')

    redial_delay = models.IntegerField(default=30,
        help_text='''Number of minutes to wait before calling again (mainly for phone calls)''')

    working_day_starts = models.PositiveIntegerField(default=8,
        validators=[is_24_hour], help_text="""Hour (24h clock) at which phone
            calls and texts should start to be made""")

    working_day_ends = models.PositiveIntegerField(default=22,
       validators=[is_24_hour], help_text="""Hour (24h clock) at which phone
            calls and texts should stop.""")

    def in_working_hours(self, hour=None):
        """Return True if we are within the study's working hours.

        Working hours are defined by the `working_day_starts` and
        `working_day_ends` fields."""

        hour = hour or datetime.now().time().hour
        workinghours = range(
            self.working_day_starts, self.working_day_ends - 1)
        if hour in workinghours:
            return True
        return False

    show_study_condition_to_user = models.BooleanField(default=False,
        help_text="""If True, the user will be able to see their condition on
        their homepage. Useful primarily for experiments where participants
        signs up with the experimenter present and where blinding is not a
        concern (e.g. where the experimenter carries out one of several
        manipulations).""")

    randomisation_probability = models.DecimalField(
        max_digits=2, decimal_places=1, default=.5,
        help_text="""Indicates the probability that the adaptive algorithm will
        choose weighted randomisation rather than allocation to the group which
        minimises the imbalance (minimisation or adaptive randomisation).
        For example, if set to .5, then deterministic allocation to the
        smallest group will only happen half of the time. To turn off adaptive
        randomisation set to 1.""")

    visible_profile_fields = models.CharField(max_length=200,
        blank=True, null=True, help_text="""Available profile fields
        for this study. Can be any of: {0}, separated by a space.""".format(
        ", ".join(settings.USER_PROFILE_FIELDS)),
        validators=[only_includes_allowed_fields])

    required_profile_fields = models.CharField(max_length=200,
        blank=True, null=True, help_text="""Profile fields which users
        will be forced to complete for this study. Can be any of: {0},
        separated by a space.""".format(", ".join(settings.USER_PROFILE_FIELDS)),
        validators=[only_includes_allowed_fields])

    valid_telephone_country_codes = models.CommaSeparatedIntegerField(max_length=32, default="44",
        help_text="""Valid national dialing codes for participants in this study.""")

    def profile_fields_dict(self):
        vis = self.visible_profile_fields or ""
        req = self.required_profile_fields or ""
        return {
            'visible': set(vis.split() + req.split()),
            'required': req.split()
        }

    def randomised(self):
        """Return the Memberships which have been randomised to a Condition in this Study."""

        return self.membership_set.filter(date_randomised__isnull=False)

    def unrandomised(self):
        """Return a Queryset of participants NOT randomised to a Condition."""

        return self.membership_set.filter(date_randomised__isnull=True)

    def scripts_used_by_this_study(self):
        return set(
            itertools.chain(
                *[i.scripts.all() for i in self.studycondition_set.all()])
        )

    def askers_used_by_this_study(self):
        askers = itertools.chain(*[[i.asker for i in j.scripts.all() if i.asker]
                                   for j in self.studycondition_set.all()])
        return set(askers)

    def questions_used(self):
        """Return all :class:`Question`s used to record an :class:`Answer` for this class:`Study`."""

        answers = Answer.objects.filter(reply__observation__dyad__study=self)
        questions = [i.question for i in answers if i.question]

        return list(set(questions))

    def observations_with_duplicate_replies(self):
        Observation = get_model('signalbox', 'Observation')
        obs = Observation.objects.filter(dyad__study=self)
        dupes = obs.annotate(
            num_replies=Count('reply')).filter(num_replies__gt=1)
        return dupes

    def unresolved_observations_with_duplicate_replies(self):
        obs = self.observations_with_duplicate_replies()
        unresolved = [i for i in obs if i.reply_set.filter(
            is_canonical_reply=True).count() == 0]
        return unresolved

    def observations(self):
        Observation = get_model('signalbox', 'Observation')
        return Observation.objects.filter(dyad__study=self)

    class Meta:
        app_label = 'signalbox'
        ordering = ["name"]
        verbose_name_plural = "studies"

    @contract
    def chisq_imbalance(self):
        """Returns the chi2 and p value for the imbalance in allocations.

        That is, between current membership allocations and the expected
        frequencies based on the StudyCondition weights.

        :rtype: tuple(float, float)
        """
        conditions = self.studycondition_set.all()
        counts = [i.users.count() for i in conditions]
        expected =  [i.expected_n() for i in conditions]

        return chisquare(counts, expected)


    def get_absolute_url(self):
        return reverse('study', args=(self.pk,))

    def clean(self, *args, **kwargs):

        if self.auto_randomise is False and self.auto_add_observations is True:
            raise ValidationError("""Observations can only be added automatically
                when participants are automatically randomised to a condition.""")

        needtwilio = bool(sum(map(lambda x: x.script_type.require_study_ivr_number, self.scripts_used_by_this_study())))
        if needtwilio and not self.twilio_number:
            raise ValidationError("This study uses Scripts which will make calls and require Twilio account details.")

        super(Study, self).clean(*args, **kwargs)

    def __unicode__(self):
        return self.name


class StudyCondition(models.Model):
    '''Groupings of participants within a study.'''
    study = models.ForeignKey('signalbox.Study', blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')
    tag = models.SlugField(max_length=255, default="main")
    display_name = models.CharField(max_length=30, blank=True, null=True,
                                    help_text="""A label for this condition which can be shown to
        the Participant (e.g. a non-descriptive name used to identify a
        condition in an experimental session without breaking a blind.""", )
    weight = models.IntegerField(default=1,
                                 help_text="""Relative weights to allocate users to conditions""")
    scripts = models.ManyToManyField('signalbox.Script', blank=True, null=True)


    def expected_n(self):
        """Return the expected number of participants based on the total currently allocated to the parent study."""
        weights = [i.weight for i in self.study.studycondition_set.all()]
        w = self.weight/sum(weights)
        return self.study.membership_set.count() * w

    class Meta:
        ordering = ['study', 'tag']
        app_label = 'signalbox'

    def __unicode__(self):
        return "%s > %s " % (self.study.name, self.tag)
