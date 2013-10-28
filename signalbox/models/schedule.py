#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.template import Context, Template
from django.contrib.humanize.templatetags.humanize import ordinal
from django.db import models
from django.core.exceptions import ValidationError

from dateutil import *
from dateutil.parser import *
from dateutil.rrule import *
from datetime import datetime, timedelta, time
import datetime as dtmod
from dateutil_constants import *
import itertools as it
from signalbox.utils import csv_to_list
import validators as v
from signalbox.utilities.linkedinline import admin_edit_url
from naturaltimes import parse_natural_date
from signalbox.utilities.djangobits import render_string_with_context, safe_help




NATURAL_DATE_SYNTAX_HELP = safe_help(u"""
Each line in this field will be read as a date on which to make an observation
when the script is executed. By default each date is created relative to the
current date and time at midnight. For example, if a user signed up when this
page loaded, these lines:

<code>now</code>, <code>next week</code>, and <code>in 3 days at 5pm</code>
would create the following dates: <div id="exampletimes">.</div>


<input type=hidden id="examplesyntax" value="now \n next week \n in 3 days at 5pm">
<script type="text/javascript">
$.post("/admin/signalbox/preview/timings/",
    {'syntax': $('#examplesyntax').val() },
    function(data) { $('#exampletimes').html(data);}
);
</script>

<div class="alert">
<i class="icon-warning-sign"></i>
Note that specifying options here will override other
advanced timing options specified in other panels.</div>

<a class="btn timingsdetail" href="#"
    onclick="$('.timingsdetail').toggle();return false;">Show more examples</a>

<div class="hide timingsdetail">

Other examples include:

<pre>
    3 days from now
    a day ago
    in 2 weeks
    in 3 days at 5pm
    now
    10 minutes ago
    10 minutes from now
    in 10 minutes
    in a minute
    in 30 seconds
    tomorrow at noon
    tomorrow at 6am
    today at 12:15 AM
    2 days from today at 2pm
    a week from today
    a week from now
    3 weeks ago
    next Sunday at noon
    Sunday noon
    next Sunday at 2pm
</pre>

HOWEVER - you must check the times have been interpreted properly before using
the script.
</div>

""")


class ScriptType(models.Model):
    """Defines what gets created by a Script."""

    name = models.CharField(max_length=255)
    observation_subclass_name = models.CharField(blank=True, max_length=255)
    require_study_ivr_number = models.BooleanField(default=False)
    sends_message_to_user = models.BooleanField(default=True, help_text="""True
        if observations created with this type of script send some form of
        message to a user (e.g. email, sms or phone calls).""")

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'signalbox'


class Reminder(models.Model):
    """Describes a reminder (c.f. ReminderInstance, ScriptReminder)"""

    name = models.CharField(max_length=50)

    kind = models.CharField(max_length=100,
                            choices=((i, i) for i in ["sms", "email"]), default="email")

    from_address = models.EmailField(blank=True,
                                     help_text=safe_help("""
The email address you want the reminder to appear as if it
has come from. Think carefully before making this something other than
your own email, and be sure the smpt server you are using will accept
this  as a from address (if you're not sure, check). If blank this will be the
study email. For SMS reminders the callerid will be the SMS return number
specified for the Study."""))

    subject = models.CharField(max_length=1024, blank=True,
                               verbose_name="Reminder email subject",
                               help_text="""For reminder emails only""")

    message = models.TextField(blank=True, help_text="""The body of the message.
        See the documentation for message_body fields on the Script model for
        more details. You can include some variable with {{}} syntax, for
        example {{url}} will include a link back to the observation.""",
                               verbose_name="Reminder message")

    def admin_edit_url(self):
        return admin_edit_url(self)

    class Meta:
        app_label = 'signalbox'

    def __unicode__(self):
        return self.name


class ScriptReminder(models.Model):
    """Link Model between Reminders and Scripts (c.f. ReminderInstance)"""

    hours_delay = models.PositiveIntegerField(default="48")
    script = models.ForeignKey('signalbox.Script')
    reminder = models.ForeignKey(Reminder)

    def calculate_date(self, observation):
        return observation.due + timedelta(hours=self.hours_delay)

    def admin_edit_url(self):
        return admin_edit_url(self, indirect_pk_field="reminder")

    class Meta:
        app_label = 'signalbox'

    def __unicode__(self):
        return """%s attached to %s""" % (self.reminder, self.script)


class Script(models.Model):
    """Defines :class:`Observation`s to be made and a schedule to make them.

    Scripts are attached to :class:`StudyCondition`s and used when
    :class:`Observation's are being added for a :class:`Membership` to determine
    a schedule of measurements.

    Scripts specify repeating rules using the python `dateutil` library.
    dateutil syntax can either be used directly (in the `raw_date_syntax` field)
    or by  completing the `repeat_by...` fields, which are combined to generate
    a repeating rule.

    Care (and some mental effort) needs to be taken when generating repeating
    rules that the schedule is as expected --- it's actually a complicated
    problem, and dateutil is very general and abstract in what it allows, which
    means most things are possible, but at the cost of complexity. In
    particular, fields like `repeat_bymonths` can interact with other options to
    create slightly counterintuitive results. When editing a Script in the
    django admin, a preview  of dates and times to be generated is available.
    However you should consider the possibility that times between observations,
    or the latency for the first observation,  may differ based on when the user
    is randomised. A simple example: if an observation is to be repeated by hour
    at 9am, a user signing up at 8am will recieve an observation right away,
    whereas one signing up at 10am will recieve their first only the next day.

    ..note:: It may often be a good idea to split observations across multiple
    scripts to avoid having to write very complicated repeating rules. """

    name = models.CharField(max_length=200, unique=False,
                            help_text="""This is the name participants will see""")

    reference = models.CharField(max_length=200, unique=True, null=True,
                                 help_text="""An internal reference. Not shown to participants.""")

    admin_display_name = lambda self: self.reference or self.name
    admin_display_name.short_description = "Reference/Name"
    admin_display_name.admin_order_field = 'reference'

    is_clinical_data = models.BooleanField(default=False, help_text="""
        If checked, indicates only clinicians and superusers should
        have access to respones made to this script.""")

    breaks_blind = models.BooleanField(default=True,
                                       help_text="""If checked, indicates that observations created by this
        Script have the potential to break the blind. If so, we will exclude
        them from views which Assessors may access.""")

    show_in_tasklist = models.BooleanField(
        verbose_name="Show in user's list of tasks to complete",
        default=True,
        help_text="""Should :class:`Observation`s generated by this script
        appear in  a user's list of tasks to complete.""")

    allow_display_of_results = models.BooleanField(default=False,
        help_text="""If checked, then replies to these observations may be
        visible to some users in the Admin area (e.g. for screening
        questionnaires). If unchecked then only superusers will be able to
        preview replies to observations made using this script.""")

    show_replies_on_dashboard = models.BooleanField(default=True,
        help_text="""If true, replies to this script are visible to the user
        on their personal dashboard.""")

    script_type = models.ForeignKey(ScriptType,
        help_text="""IMPORTANT: This type attribute determines the
        interpretation of some fields below.""")

    asker = models.ForeignKey('ask.Asker', blank=True, null=True,
        help_text="""Survey which the participant will complete for the
        Observations created by this script""",
        verbose_name="Attached questionnaire")

    external_asker_url = models.URLField(blank=True, null=True,
            verbose_name="Externally hosted questionnaire url",
            help_text="""The full url of an external questionnaire. Note that
            you can include {{variable}} syntax to identify the Reply or
            Observation from which the user has been redirected. For example
            including http://monkey.com/survey1?c={{reply.observation.dyad.user.username}}
            would pass the username of the study participant to the external system.
            In contrast including {{reply.observation.id}} would simply pass the
            anonymous Observation id number. Where a questionnaire will be
            completed more than once during the study, it iss recommended to
            include the {{reply.id}} or {{reply.token}} to allow for reconciling
            external data with internal data at a later date.""")

    def parse_external_asker_url(self, reply):
        return render_string_with_context(self.external_asker_url, {'reply': reply})

    label = models.CharField(max_length=255, blank=True,
        default="{{script.name}}",
        help_text=safe_help("""This field allows individual observations to have a
        meaningful label when listed for participants.  Either enter a simple
        text string, for example "Main questionnaire", or have the label created
        dynamically from information about this script object.

For example, you can enter `{{i}}` to add the index in of a particular
observation in a sequence  of generated observations. If you enter `{{n}}`
then this will be the position ('first', 'second' etc.).

Advanced use: If you want to reference attributes of the Script or Membership
objects these are passed in as extra context, so {{script.name}}
includes the script name, and `{{membership.user.last_name}}` would
include the user's surname. Mistakes when entering  these variable names
will not result in an error, but won't produce any output either. """))

    script_subject = models.CharField(max_length=1024, blank=True,
                                      verbose_name="Email subject",
                                      help_text="""Subject line of an email if required. Can use django
        template syntax to include variables: {{var}}. Currently variables
        available are {{url}} (the link to the questionnaire), {{user}} and
        {{userprofile}} and {{observation}}.""")

    script_body = models.TextField(blank=True,
        help_text="""Used for Email or SMS body. Can use django template syntax
        to include variables: {{var}}. Currently variables available are {{url}}
        (the link to the questionnaire), {{user}} and {{userprofile}} and
        {{observation}}. Note that these are references to the django objects
        themselves, so you can use the dot notation to access other attributed.
        {{user.email}} or {{user.last_name}} for example, would print the user's
        email address or last name.""", verbose_name="Message")

    user_instructions = models.TextField(blank=True, null=True,
                                         help_text="""Instructions shown to user on their homepage and perhaps
        elsewhere as the link to the survey. For example, "Please fill in the
        questionnaire above. You will need to allow N minutes to do this  in
        full." """)

    max_number_observations = models.IntegerField(default=1,
                                                  help_text="""The # of observations this scipt will generate.
            Default is 1""", verbose_name="""create N observations""")

    RRULES = [(i, i) for i in "YEARLY MONTHLY WEEKLY DAILY HOURLY MINUTELY SECONDLY".split(" ")]

    repeat = models.CharField(max_length=80, choices=RRULES, default='DAILY')

    repeat_from = models.DateTimeField(blank=True, null=True,
                                       verbose_name="Fixed start date",
                                       help_text="""Leave blank for the observations to start relative to the
        datetime they are  created (i.e. when the participant is randomised)""")

    repeat_interval = models.IntegerField(blank=True, null=True,
                                          help_text="""The interval between each freq iteration. For example,
        when repeating WEEKLY, an interval of 2 means once per fortnight,
        but with HOURLY, it means once every two hours.""",
                                          verbose_name="repeat interval")

    repeat_byhours = models.CommaSeparatedIntegerField(blank=True, null=True,
       max_length=20,
       validators=[v.valid_hours_list],
       help_text="""A number or list of integers, indicating the hours of the
       day at which observations are made. For example, '13,19' would make
       observations happen at 1pm and 7pm.""",
       verbose_name="repeat at these hours")

    def repeat_byhours_list(self):
        return [int(i) for i in csv_to_list(self.repeat_byhours) if int(i) < 24]

    repeat_byminutes = models.CommaSeparatedIntegerField(blank=True, null=True,
        max_length=20,
        validators=[
        v.in_minute_range],
        help_text="""A list of numbers indicating at what minutes past the
        hour the observations should be created. E.g. 0,30 will create
        observations on the hour and half hour""",
        verbose_name="repeat at these minutes past the hour")

    def repeat_byminutes_list(self):
        return [int(i) for i in csv_to_list(self.repeat_byminutes)]

    repeat_bydays = models.CharField(blank=True, null=True, max_length=100,
                                     help_text="""One or more of MO, TU, WE, TH, FR, SA, SU separated by a
        comma, to indicate which days observations will be created on.""",
                                     verbose_name="repeat on these days of the week")

    def repeat_bydays_list(self):
        return [WEEKDAY_MAP[i.strip()[0:2]] for i in csv_to_list(self.repeat_bydays)]

    repeat_bymonths = models.CommaSeparatedIntegerField(blank=True,
                                                        null=True, max_length=20,
                                                        help_text="""A comma separated list of months as numbers (1-12),
        indicating the months in which obervations can be made. E.g. '1,6' would
        mean observations are only made in Jan and June.""",
                                                        verbose_name="repeat in these months")

    def repeat_bymonths_list(self):
        return [int(i) for i in csv_to_list(self.repeat_bymonths)]

    repeat_bymonthdays = models.CommaSeparatedIntegerField(blank=True,
                                                           null=True, max_length=20,
                                                           help_text="""An integer or comma separated list of integers; represents
        days within a  month on observations are created. For example, '1, 24'
        would create observations on the first and 24th of each month.""",
                                                           verbose_name="on these days in the month")

    def repeat_bymonthdays_list(self):
        return [int(i) for i in csv_to_list(self.repeat_bymonthdays)]

    delay_by_minutes = models.IntegerField(default=0, help_text="""Start the
        observations this many minutes from the time the Observations are added.""")

    delay_by_hours = models.IntegerField(default=0, help_text="""Start the
        observations this many hours from the time the Observations are added.""")

    delay_by_days = models.IntegerField(default=0, help_text="""Start the
        observations this many days from the time the Observations are added.""")

    delay_by_weeks = models.IntegerField(default=0, null=True, help_text="""Start the
        observations this many weeks from the time the Observations are added.""")

    delay_in_whole_days_only = models.BooleanField(default=True,
                                                   help_text="""If true, observations are delayed to the nearest number of
        whole days, and repeat rules will start from 00:00 on the morning of
        that day.""")

    def delay(self):
        """Calculate the interval until Observations start.

        Returns a dateime.TimeDelta object"""

        return timedelta(weeks=self.delay_by_weeks,
                         days=self.delay_by_days,
                         hours=self.delay_by_hours,
                         minutes=self.delay_by_minutes)

    natural_date_syntax = models.TextField(blank=True, null=True,
                                           validators=[
                                           v.valid_natural_datetime],
                                           help_text=NATURAL_DATE_SYNTAX_HELP)

    def eval_natural_date_synax(self):

        timesanderrors = [parse_natural_date(t)
                          for t in self.natural_date_syntax.splitlines()]

        times = [i for i, e in timesanderrors if not e]
        return times

    completion_window = models.IntegerField(blank=True, null=True,
                                            help_text="""Window in minutes during which the observation can be
        completed. If left blank, the observation will not expire.""")

    jitter = models.IntegerField(blank=True, null=True,
                                 help_text="""Number of minutes (plus or minus) to randomise observation
        timing by.""")

    reminders = models.ManyToManyField(Reminder, through=ScriptReminder)

    def calculate_start_datetime(self, start_date=None):
        """Return the date the observations should start on."""

        start_date = start_date or datetime.now()

        # we pass in date_randomised sometimes, which is a date not a datetime
        # so here we convert it if needed
        if type(start_date) == dtmod.date:
            start_date = datetime.combine(start_date, time())

        startfrom = start_date + self.delay()

        if self.delay_in_whole_days_only:
            return startfrom.replace(hour=0, minute=0, second=0, microsecond=0)

        return startfrom

    def datetimes_with_natural_syntax(self):
        datesyntax = self.natural_date_syntax or "ADVANCED"
        return [{'datetime': i, 'syntax': j} for i, j, k in
                it.izip_longest(self.datetimes(), datesyntax.split("\n"), "")]

    def preview_of_datetimes(self):
        code = lambda x: "<code>" + str(x) + "</code>"
        return safe_help("<br>".join(map(code, list(self.datetimes()))))
    preview_of_datetimes.allow_tags = True

    def datetimes(self, start_date=None):

        if self.natural_date_syntax:
            return self.eval_natural_date_synax()
        else:
            kwargs = {
                'count': self.max_number_observations,
                'interval': self.repeat_interval,
                'byhour': self.repeat_byhours_list(),
                'byminute': self.repeat_byminutes_list(),
                'byweekday': self.repeat_bydays_list(),
                'bymonth': self.repeat_bymonths_list(),
                'bymonthday': self.repeat_bymonthdays_list(),
                'dtstart': self.calculate_start_datetime(start_date=start_date)
            }
            # filter out properties with null values
            kwargs = dict([(k, v) for k, v in kwargs.items() if v])

            # return an rrule iterator containing the dates
            return rrule(FREQ_MAP[self.repeat], **kwargs)

    def make_observations(self, membership):

        from signalbox.models import Observation

        times = self.datetimes(membership.date_randomised)
        times_indexes = zip(times, xrange(1, len(list(times)) + 1))

        observations = []
        for time, index in times_indexes:
            observations.append(
                Observation(due_original=time,
                    n_in_sequence=index,
                    label=render_string_with_context(self.label,
                                {'i': index,
                                'n': ordinal(index),
                                 'script': self,
                                 'membership': membership
                                }),
                    dyad=membership,
                    created_by_script=self)
                )

        [i.save() for i in observations]

        return observations

    class Meta:
        ordering = ['reference', 'name']
        app_label = 'signalbox'

    def clean(self):
        if self.asker and self.external_asker_url:
            raise ValidationError("""You can't use both an internal
                                    Questionnaire and one hosted on an external site.""")

        if self and self.script_type and self.script_type.name == "TwilioSMS":
            if len(self.script_body) > 160:
                raise ValidationError(
                    "Messages must be < 160 characters long.")

    def __unicode__(self):
        return u'(%s) %s' % (self.reference, self.name)
