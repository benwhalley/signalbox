import random
import itertools
import twilio

from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from django_extensions.db.fields import UUIDField
from django.db import models

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.urlresolvers import reverse
from django.conf import settings

from jsonfield import JSONField
from signalbox.utilities.linkedinline import admin_edit_url
from signalbox.utilities.sanitise_redirects import sanitise_user_supplied_redirect
from ask.models import Question
from signalbox.exceptions import CategoryErrorException
from signalbox.utils import pretty_datetime, current_site_url
import  observation_timing_functions as tf
import observation_methods.default as default
import observation_helpers as hlp
from reply import Reply
from answer import Answer
from schedule import ScriptReminder
from signalbox.utilities.djangobits import supergetattr


def import_module_by_string(name):
    """str -> module. Returns the module object identified by name."""
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class ReminderInstance(models.Model):
    """Reminders, created for observations, by Reminders attached to Scripts"""

    reminder = models.ForeignKey('signalbox.Reminder')
    observation = models.ForeignKey('signalbox.Observation')
    due = models.DateTimeField(db_index=True)
    sent = models.BooleanField(default=False, db_index=True)

    def send_reminder(self):
        """Does the sending a reminder, using context from the observation."""

        # call the right function for the type of reminder
        if self.observation.status == 1:
            return (False, "Observation already complete")

        if not self.observation.dyad.active:
            return (False, "Membership is inactive.")

        success, statusmessage = getattr(self,
            "_send_%s_reminder" % (self.reminder.kind, ))()
        self.sent = success
        self.save()

        return (bool(success), str(statusmessage))

    def _send_email_reminder(self):
        """Send an email reminder -> (bool_success, str_statusmessage)"""

        
        to_address, from_address = hlp.get_email_address_details(self.observation)
        from_address = self.reminder.from_address or from_address  # override if needed
        
        subject, message = hlp.format_message_content(self.reminder.subject,
            self.reminder.message, self.observation)

        success, statusmessage = hlp.send_email(to_address, from_address, subject, message)
        self.observation.add_data(key="reminder", value=subject + "\n" + message)
        return (bool(success), str(statusmessage))

    def _send_sms_reminder(self):

        client = self.observation.dyad.study.twilio_number.client()

        to_number = self.observation.user.get_profile().mobile()
        from_number = self.observation.dyad.study.twilio_number.number()
        _, message = hlp.format_message_content("", self.reminder.message, self.observation)

        try:
            result = client.sms.messages.create(to=to_number, from_=from_number, body=message,
                    status_callback=current_site_url() + reverse('sms_callback'))
            self.observation.add_data(key="external_id", value=result.sid)
            self.observation.add_data(key="reminder",
                value="%s (sent to number ending %s)" % (message, to_number[-3:]))

            return (True, str(result.sid))

        except twilio.TwilioException as e:
            return (False, str(e))

    class Meta:
        app_label = 'signalbox'

    def __unicode__(self):
        return u"%s (reminder) due at %s" % (self.reminder, pretty_datetime(self.due))


class ObservationManager(models.Manager):
    """A manager to ensure user roles are respected when querying observations."""

    def personalised(self, user, due_now=False):
        allobs = super(ObservationManager, self).get_query_set().order_by('-due')

        if not user.is_staff:
            # only show your own
            return allobs.filter(dyad__user=user)

        if due_now:
            allobs = allobs.filter(due__lt=datetime.now() + timedelta(days=1))

        if user.groups.filter(name="Assessors").count() > 0:
            allobs = allobs.exclude(
                created_by_script__isnull=True).exclude(
                    created_by_script__breaks_blind=True
                )

        return  allobs


class Observation(models.Model):
    """
    An Observation defines an occasion the system will collect data, and how.

    Observations are created by Scripts which can be attached to StudyConditions.

    """

    objects = ObservationManager()

    label = models.CharField(blank=True, null=True, max_length=1024, help_text="""The
        text label displayed to participants in listings.""")

    n_in_sequence = models.IntegerField(blank=True, null=True, help_text="""Indicates what position in the
        sequence of Observations created by the Script this observation is.""")

    dyad = models.ForeignKey('signalbox.Membership', blank=True, null=True)

    created_by_script = models.ForeignKey('signalbox.Script',
        blank=True, null=True, editable=False)

    status = models.IntegerField(choices=settings.STATUS_CHOICES, default=0, db_index=True)

    due_original = models.DateTimeField(
        help_text="Original scheduled time to make this Observation.",
        verbose_name="time scheduled", db_index=True)

    due = models.DateTimeField(help_text="""Time the Obs. will actually be made.
        This can be affected by many things including user requests for a later call""",
        verbose_name="time due", db_index=True, null=True)
    # due set to null=True because of this bug https://code.djangoproject.com/ticket/12627
    # the problem is that the ObservationAdmin has all fields set to readonly, which
    # in turn breaks the date_hierarchy filter unless this is set to nullable.

    last_attempted = models.DateTimeField(blank=True, null=True, db_index=True)

    offset = models.IntegerField(blank=True, null=True,
        help_text="""Offset added to deterministic time by using the random
        `jitter' parameter of the parent rule.""",
        verbose_name="random offset")

    attempt_count = models.IntegerField(default=0, db_index=True)

    token = UUIDField()

    def add_reminders(self):
        scriptreminders = ScriptReminder.objects.filter(script=self.created_by_script)
        instances = [ReminderInstance(
            reminder=i.reminder,
            observation=self,
            due=i.calculate_date(self)) for i in scriptreminders]

        [i.save() for i in instances]
        return instances

    def add_jitter(self, jitter):
        """Add noise to the scheduled time for this observation, based on Script settings."""
        if self.created_by_script.jitter:
            scr = self.created_by_script
            self.offset = random.randrange(-scr.jitter, scr.jitter)
            self.due = self.due_original = self.due_original + timedelta(minutes=self.offset)

    def has_manually_selected_canonical_reply(self):
        allreplies = self.reply_set.all().order_by('-last_submit')
        canon = allreplies.filter(is_canonical_reply=True)
        return bool(canon.count())

    def canonical_reply(self):
        """Returns the most authoritative Reply for the Observation.

        Either a Reply marked as canonical by an admin, or the last-submitted Reply
        """

        allreplies = self.reply_set.all().order_by('-last_submit')
        #Reply.objects.filter(observation=self).order_by('-last_submit')
        canon = allreplies.filter(is_canonical_reply=True)
        if len(canon) > 0:
            return canon[0]
        if len(allreplies) > 0:
            return allreplies[0]
        return None

    @property
    def asker(self):
        """Return the Asker associated with this Observation (if any)"""

        if self.created_by_script:
            return self.created_by_script.asker
        else:
            return None

    def timeshift_allowed(self):
        """Determine whether Researchers can timeshift this observation -> Boolean"""

        return self.reply_set.all().count() == 0

    def add_data(self, key, value=""):
        data = ObservationData(observation=self, key=key, value=value)
        data.save()
        return True

    @property
    def user(self):
        return self.dyad.user

    def script(self):
        if self.created_by_script:
            return self.created_by_script
        else:
            return None

    def script_type(self):
        if self.script():
            return self.script().script_type
        return None

    def status_string(self):
        return settings.STATUS_CHOICES_DICT[self.status]

    def due_display_date(self):
        """Return the date to display as the "due date" for this observation."""

        return self.open_until() or self.due

    def days_hours_remaining(self):
        closes = self.open_until()
        if not closes:
            return (None, None)
        delta = self.open_until() - datetime.now()
        return (delta.days, delta.seconds / 60 / 60)

    def expires_today(self):
        days, hours = self.days_hours_remaining()
        return days == 0

    def display_time_remaining(self):

        days, hours = self.days_hours_remaining()
        if days > 0:
            return "{} days {} hours remaining".format(days, hours)
        elif hours:
            return "{} hours remaining".format(hours)
        else:
            return ""

    def open_until(self):
        """Return the last date/time this observation can be completed."""

        if not (self.created_by_script and self.created_by_script.completion_window):
            return None
        delta = timedelta(minutes=self.created_by_script.completion_window)
        return self.due + delta

    def still_open(self):
        """Check the Observation has not expired; return boolean."""

        closes = self.open_until()
        if not closes:
            return True

        return bool((self.due < datetime.now()) and
            (datetime.now() < closes))

    def curfew_applies(self):
        """Check that we are not within the study curfew (for calls and texts)"""

        is_restricted_type = self.script_type() in ['TwilioCall', 'TwilioSMS']
        curfew_is_on = not self.dyad.study.in_working_hours()

        return bool(is_restricted_type and curfew_is_on)
    curfew_applies.boolean = True

    def study_paused(self):
        """Check the Observation doesn't belong to a paused study -> Boolean.
        """
        return self.dyad.study.paused

    def membership_active(self):
        """Check if this study membership has been paused -> Boolean."""
        if self.dyad:
            return bool(self.dyad.active)
        else:
            return True
    membership_active.boolean = True

    n_questions = models.IntegerField(blank=True, null=True)
    n_questions_incomplete = models.IntegerField(blank=True, null=True)

    def completion_data(self):
        """Returns tuple: (N questions answered, N questions to complete)."""

        if not self.asker:
            return (None, None)

        available_questions = self.asker.questions()
        answered = Answer.objects.select_related(
            ).filter(reply__observation=self
            ).exclude(other_variable_name="page_id"
            )

        answered_questions = set(
            [(i.question, i.other_variable_name) for i in answered]
        )

        try:
            incomplete = len(available_questions) - len(answered_questions)
        except TypeError:
            incomplete = None

        return (len(available_questions), len(available_questions), incomplete)

    def _ready_prelims(self):
        """Tests common to both ready_for_reminder and ready_to_send -> Boolean."""

        bools = []
        bools.append(bool(self.due < datetime.now()) is True)
        bools.append(self.study_paused() is False)
        bools.append(self.still_open() is True)
        bools.append(self.curfew_applies() is False)
        bools.append(self.membership_active() is True)

        return False not in bools

    def ready_to_send(self):
        """Check if Observation is due to be made -> Boolean."""

        if self.created_by_script is None:
            return True

        bools = []
        bools.append(self._ready_prelims())
        bools.append(tf.is_pending(self) is True)

        # todo XXX... reinstate this, but only for phone calls
        # bools.append(tf.wait_period_expired(self) is True)
        # see disabled tests in test_not_resending_observation()
        bools.append(tf.less_than_max_attempts(self) is True)

        return False not in bools
    ready_to_send.boolean = True

    def increment_attempts(self):
        """Record that the Observation was attempted."""
        self.attempt_count += 1
        return self.save()

    def get_extra_time(self):
        return self.created_by_script.redial_delay

    def save(self, *args, **kwargs):
        '''Redefine save to manage Observation entries.'''

        self.due = self.due or self.due_original
        super(Observation, self).save(*args, **kwargs)

    def create_observation_context(self):
        """Return a dictionary which can be used as in a Context() call to fill in templates."""

        url = None
        if self.link():
            url = current_site_url() + self.link()

        return {
            'url': url,
            'observation': self,
            'study': self.dyad.study,
            'script': self.created_by_script,
            'user': self.dyad.user,
            'userprofile': self.dyad.user.get_profile(),
        }

    def can_resend(self):
        """Return true if a message can be sent to the user."""
        return bool(self.asker)

    def can_add_answers(self):
        """Return true if questions can be answered in response to this Observation"""
        return bool(self.asker or self.created_by_script.external_asker_url)

    def open_for_data_entry(self, request=None):
        """
        Checks if it's OK for data to be added to this Observation in this http request.

        Returns (Bool, Message) indicating whether the user is allowed to enter data.

        Default is to allow data entry, to avoid false positives.

        If we don't pass in a request all the other checks are made and a boolean
        returned based on those, but we don't check user has double entry permissions.
        """

        if (request and (request.user.has_perm('signalbox.can_double_enter')
                or request.user.is_superuser)):
            return True, ""

        if self.status == 1:
            return False, "You've already completed this survey."

        if not self.still_open:
            return False, """The gap between recieving your email or SMS and answering the
                question was too long. Please wait for the next signal to complete your
                next task."""

        if not self.ready_to_send:
            return False, """This page is not available yet."""

        return (True, "")

    def make_reply(self, request, external_id=None, success_url=None, entry_method=None):
        """Makes a new reply: Returns a tuple: (Reply, bool_is_new_reply)"""
        if not self.can_add_answers():
            raise CategoryErrorException("No answers can be added for this type of observation.")

        # if we don't do this we get the curse of SimpleLazyObject's which
        # can't be assigned to the user fk column of the reply
        loggedin = request.user.is_authenticated()
        user = (loggedin and request.user) or None

        reply, isnew = Reply.objects.get_or_create(
            asker=self.asker,
            observation=self,
            user=user,
            external_id=external_id,
            entry_method=entry_method,
            complete=False
        )

        if not isnew:
            messages.add_message(request, messages.SUCCESS, "resuming data entry")

        # determine where to redirect to
        if success_url:
            reply.redirect_to = sanitise_user_supplied_redirect(request, success_url)
        elif reply.entry_method is "double_entry":
            reply.redirect_to = reverse('check_double_entry', args=(reply.id,))

        reply.save()
        return reply

    def variables_which_differ_between_multiple_replies(self):
        """-> queryset of Questions

        Where an observation has multiple replies, different questions may have been answered
        in each reply, or different answers given to the same question. This function identifies
        variables which have different or missing responses across replies, and returns a queryset
        of the Questions which differ.
        """
        replies = self.reply_set.all()
        if replies.count() < 2:
            return []
        answer_sets = [set(reply.answer_set.all().values_list('question__id', 'answer'))
            for reply in replies]

        diffs = [i[0].symmetric_difference(i[1]) for i in itertools.combinations(answer_sets, 2)]

        if len(diffs) > 0:
            diffs = list(itertools.chain(*diffs))

        question_ids = set([i for i, _ in diffs])
        return Question.objects.filter(id__in=question_ids)

    def model_name(self):
        return self.created_by_script.script_type.observation_subclass_name

    def helper_module(self):
        """Import the observation_methods module to override methods like do()

        Methods described below are either imported from the observation_methods.default
        module, or from a specific module for the type of observation (e.g. "Email").
        """

        return import_module_by_string("signalbox.models.observation_methods." + self.model_name())

    def admin_edit_url(self):
            return admin_edit_url(self)

##################################################################################################
    #
    # NOTE: the following functions are defined externally and brought in based on the script_type
    #
##################################################################################################

    def do(self, *args, **kwargs):
        """Do this observation - that is, send the email, make the call etc."""
        if self.created_by_script:
            return getattr(self.helper_module(), 'do', default.do)(self, *args, **kwargs)

    def link(self, **kwargs):
        """Return a url to complete the Observation at."""
        return getattr(self.helper_module(), 'link', default.link)(self, **kwargs)

    def update(self, success_status):
        """Updates the Observation when do() is called.
        """

        return getattr(self.helper_module(), 'update', default.update)(self, success_status)

    def show_in_tasklist(self):
        """Check whether user should see this in their tasks listing; return boolean."""

        if self.created_by_script:
            return self.created_by_script.show_in_tasklist
        return False

    def touch(self):
        """Set the last_attempt for the Observation to the current datetime."""
        return getattr(self.helper_module(), 'touch', default.touch)(self)

    def sms_replies(self):
        """A (possibly incomplete) list of SMS replies recieved via Twilio callbacks."""

        possible_sids = [i.value for i in self.observationdata_set.all()]
        sms_replies = TextMessageCallback.objects.filter(sid__in=possible_sids)
        return sms_replies

    class Meta:
        ordering = ['due']
        permissions = (
            ("can_review", "Can review progress of observations"),
            ("can_force_send", "Can force-send an Observation"),
            ("can_view_todolist", "Can see Observations due to be sent"),
        )
        app_label = 'signalbox'

    def __unicode__(self):
        return u"%s %s" % (self.id, self.label)


class ObservationData(models.Model):
    """Log objects saved each time something happens for an Observation."""

    class Meta:
        app_label = 'signalbox'

    observation = models.ForeignKey(Observation)
    key = models.CharField(max_length=255, choices=settings.OB_DATA_TYPES, db_index=True)
    value = models.TextField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.key


class TextMessageCallback(models.Model):
    sid = models.CharField(max_length=255)
    post = JSONField(blank=True, null=True, help_text="""A serialised
        request.POST object from the twilio callback""")
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    likely_related_user = models.ForeignKey(User, blank=True, null=True)

    def from_(self):
        return self.post.get('From', "")

    def to_(self):
        return self.post.get('To', "")

    def save(self, *args, **kwargs):
        # split this out to a field so we can filter on it
        self.status = self.post.get('SmsStatus', None)

        # identfify user in the system likely to have sent this message
        users = User.objects.filter(
            Q(userprofile__mobile__iendswith=self.from_()[-9:]) |
            Q(userprofile__mobile__iendswith=self.to_()[-9:])
        )
        if users.count():
            self.likely_related_user = users[0]

        super(TextMessageCallback, self).save()

    def message(self):
        return self.post.get('Body', None)

    def __unicode__(self):
        return "%s\n%s" % (self.sid, self.status)

    class Meta:
        app_label = 'signalbox'
