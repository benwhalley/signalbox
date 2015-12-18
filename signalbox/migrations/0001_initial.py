# -*- coding: utf-8 -*-


from django.db import models, migrations
import signalbox.utilities.mixins
import django_fsm.db.fields.fsmfield
import jsonfield.fields
import shortuuidfield.fields
import signalbox.s3
import signalbox.models.validators
import signalbox.models.answer
import django.db.models.deletion
import signalbox.process
import signalbox.phone_field
import django.utils.timezone
from django.conf import settings
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('twiliobox', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ask', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('mobile', phonenumber_field.modelfields.PhoneNumberField(max_length=128, null=True, blank=True)),
                ('condition', models.ForeignKey(to='ask.ShowIf')),
            ],
            options={
                'verbose_name': 'Alerting rule',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlertInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', signalbox.utilities.mixins.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', signalbox.utilities.mixins.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('viewed', models.BooleanField(default=False)),
                ('alert', models.ForeignKey(to='signalbox.Alert')),
            ],
            options={
                'verbose_name': 'Alert',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('other_variable_name', models.CharField(max_length=256, null=True, blank=True)),
                ('choices', models.TextField(help_text='JSON representation of the options the user could select from,\n        at the time the answer was saved.', null=True, blank=True)),
                ('answer', models.TextField(null=True, blank=True)),
                ('upload', models.FileField(storage=signalbox.s3.CustomS3BotoStorage(querystring_expire=300, querystring_auth=True, acl='private'), null=True, upload_to=signalbox.models.answer.upload_file_name, blank=True)),
                ('last_modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('meta', models.TextField(help_text='Additional data as python dict serialised to JSON.', null=True, blank=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='ask.AskPage', help_text='The page this question was displayed on', null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='ask.Question', help_text='The question this answer refers to', null=True)),
            ],
            options={
                'ordering': ['question__variable_name'],
                'verbose_name_plural': 'user answers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, blank=True)),
                ('followup_expected', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True)),
                ('added_by', models.ForeignKey(related_name=b'added_by', to=settings.AUTH_USER_MODEL)),
                ('participant', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('reason', models.ForeignKey(blank=True, to='signalbox.ContactReason', null=True)),
            ],
            options={
                'ordering': ['-added'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True, help_text=b'If deselected, Observations no longer be sent for Membership.', db_index=True)),
                ('date_joined', models.DateField(auto_now_add=True)),
                ('date_randomised', models.DateField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-date_randomised'],
                'verbose_name': 'Study membership',
                'permissions': (('can_add_observations', 'Can generate observations for a membership'), ('can_randomise_user', 'Can randomise a user')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(help_text=b'The\n        text label displayed to participants in listings.', max_length=1024, null=True, blank=True)),
                ('n_in_sequence', models.IntegerField(help_text=b'Indicates what position in the\n        sequence of Observations created by the Script this observation is.', null=True, blank=True)),
                ('status', models.IntegerField(default=0, db_index=True, choices=[(1, b'complete'), (0, b'pending'), (-1, b'in progress'), (-2, b'email sent, response pending'), (-3, b'due, awaiting completion'), (-4, b'redirected to external service'), (-99, b'failed'), (-999, b'missing')])),
                ('due_original', models.DateTimeField(help_text=b'Original scheduled time to make this Observation.', verbose_name=b'time scheduled', db_index=True)),
                ('due', models.DateTimeField(help_text=b'Time the Obs. will actually be made.\n        This can be affected by many things including user requests for a later call', null=True, verbose_name=b'time due', db_index=True)),
                ('last_attempted', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('offset', models.IntegerField(help_text=b"Offset added to deterministic time by using the random\n        `jitter' parameter of the parent rule.", null=True, verbose_name=b'random offset', blank=True)),
                ('attempt_count', models.IntegerField(default=0, db_index=True)),
                ('token', shortuuidfield.fields.ShortUUIDField(max_length=22, editable=False, blank=True)),
                ('n_questions', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['due'],
                'permissions': (('can_review', 'Can review progress of observations'), ('can_force_send', 'Can force-send an Observation'), ('can_view_todolist', 'Can see Observations due to be sent')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ObservationCreator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ObservationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(db_index=True, max_length=255, choices=[(b'external_id', b'External reference number, e.g. a Twilio SID'), (b'attempt', b'Attempt'), (b'reminder', b'Reminder'), (b'success', b'Success'), (b'failure', b'Failure'), (b'created', b'Created'), (b'timeshift', b'Timeshift')])),
                ('value', models.TextField(null=True, blank=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('observation', models.ForeignKey(to='signalbox.Observation')),
            ],
            options={
                'verbose_name': 'Supplementary data',
                'verbose_name_plural': 'Supplementary data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('kind', models.CharField(default=b'email', max_length=100, choices=[(b'sms', b'sms'), (b'email', b'email')])),
                ('from_address', models.EmailField(help_text="<p>The email address you want the reminder to appear as if it\nhas come from. Think carefully before making this something other than\nyour own email, and be sure the smpt server you are using will accept\nthis  as a from address (if you're not sure, check). If blank this will be the\nstudy email. For SMS reminders the callerid will be the SMS return number\nspecified for the Study.</p>", max_length=75, blank=True)),
                ('subject', models.CharField(help_text=b'For reminder emails only', max_length=1024, verbose_name=b'Reminder email subject', blank=True)),
                ('message', models.TextField(help_text=b'The body of the message.\n        See the documentation for message_body fields on the Script model for\n        more details. You can include some variable with {{}} syntax, for\n        example {{url}} will include a link back to the observation.', verbose_name=b'Reminder message', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReminderInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('due', models.DateTimeField(db_index=True)),
                ('sent', models.BooleanField(default=False, db_index=True)),
                ('observation', models.ForeignKey(to='signalbox.Observation')),
                ('reminder', models.ForeignKey(to='signalbox.Reminder')),
            ],
            options={
                'verbose_name': 'Reminder sent',
                'verbose_name_plural': 'Reminders sent',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_canonical_reply', models.BooleanField(default=False)),
                ('redirect_to', models.CharField(max_length=1000, null=True, blank=True)),
                ('last_submit', models.DateTimeField(auto_now=True, null=True)),
                ('started', models.DateTimeField(auto_now_add=True, null=True)),
                ('originally_collected_on', models.DateField(help_text=b'Set this if the date that data were entered into the system is not the date\n        that the participant originally provided the responses (e.g. when retyping paper data)', null=True, blank=True)),
                ('complete', models.BooleanField(default=False, db_index=True)),
                ('token', shortuuidfield.fields.ShortUUIDField(max_length=22, editable=False, blank=True)),
                ('external_id', models.CharField(help_text=b'Reference for external API, e.g. Twilio', max_length=100, null=True, blank=True)),
                ('entry_method', models.CharField(blank=True, max_length=100, null=True, choices=[(b'participant_ad_hoc', b'Data entered after ad-hoc script use'), (b'ad_hoc', b'DEPRECATED NAME (Ad-hoc use of questionnaire)'), (b'double_entry', b'Double entry by an administrator'), (b'twiliocall', b'Twilio telephone call'), (b'twiliosms', b'Twilio SMS conversation'), (b'anonymous', b'Anonymous survey response'), (b'participant', b'Participant via the web interface'), (b'answerphone', b'Answerphone message'), (b'preview', b'Preview'), (b'twilio', b'DEPRECATED NAME (Twilio telephone call)'), (b'ad_hoc_script', b'DEPRECATED NAME (Data entered after ad-hoc script use)')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('collector', models.SlugField(null=True, blank=True)),
                ('asker', models.ForeignKey(blank=True, to='ask.Asker', null=True)),
                ('membership', models.ForeignKey(blank=True, to='signalbox.Membership', null=True)),
                ('observation', models.ForeignKey(blank=True, to='signalbox.Observation', null=True)),
                ('user', models.ForeignKey(related_name=b'reply_user', blank=True, to=settings.AUTH_USER_MODEL, help_text=b"IMPORTANT: this is not necessarily the user providing the data (i.e. a\n        patient) but could be an assessor or admin person doing double entry from paper. It\n        could also be null, where data is added by an AnonymousUser (e.g. Twilio or external\n        API which doesn't authenticate.)", null=True)),
            ],
            options={
                'ordering': ['-started'],
                'verbose_name': 'Participant reply',
                'verbose_name_plural': 'Participant replies',
                'permissions': (('can_double_enter', 'Can add Data for another person'), ('can_resolve_duplicate_replies', 'Can resolve duplicate replies')),
            },
            bases=(models.Model, signalbox.process.ProcessManager),
        ),
        migrations.CreateModel(
            name='ReplyData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', signalbox.utilities.mixins.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', signalbox.utilities.mixins.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('key', models.CharField(db_index=True, max_length=255, choices=[(b'incorrect_response', b'incorrect_response'), (b'question_error', b'an error occured answering question with variablename')])),
                ('value', models.TextField(null=True, blank=True)),
                ('reply', models.ForeignKey(to='signalbox.Reply')),
            ],
            options={
                'get_latest_by': 'modified',
                'verbose_name': 'Reply meta data',
                'verbose_name_plural': 'Reply meta data',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScoreSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True, max_length=80, blank=True)),
                ('description', models.TextField(blank=True)),
                ('minimum_number_of_responses_required', models.IntegerField(null=True, blank=True)),
                ('function', models.CharField(max_length=200, choices=[(b'sum', b'sum'), (b'mean', b'mean'), (b'min', b'min'), (b'max', b'max'), (b'stdev', b'stdev'), (b'median', b'median')])),
                ('variables', models.ManyToManyField(related_name=b'varsinscoresheet', to='ask.Question')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'This is the name participants will see', max_length=200)),
                ('reference', models.CharField(help_text=b'An internal reference. Not shown to participants.', max_length=200, unique=True, null=True)),
                ('is_clinical_data', models.BooleanField(default=False, help_text=b'\n        If checked, indicates only clinicians and superusers should\n        have access to respones made to this script.')),
                ('breaks_blind', models.BooleanField(default=True, help_text=b'If checked, indicates that observations created by this\n        Script have the potential to break the blind. If so, we will exclude\n        them from views which Assessors may access.')),
                ('show_in_tasklist', models.BooleanField(default=True, help_text=b"Should :class:`Observation`s generated by this script\n        appear in  a user's list of tasks to complete.", verbose_name=b"Show in user's list of tasks to complete")),
                ('allow_display_of_results', models.BooleanField(default=False, help_text=b'If checked, then replies to these observations may be\n        visible to some users in the Admin area (e.g. for screening\n        questionnaires). If unchecked then only superusers will be able to\n        preview replies to observations made using this script.')),
                ('show_replies_on_dashboard', models.BooleanField(default=True, help_text=b'If true, replies to this script are visible to the user\n        on their personal dashboard.')),
                ('external_asker_url', models.URLField(help_text=b'The full url of an external questionnaire. Note that\n            you can include {{variable}} syntax to identify the Reply or\n            Observation from which the user has been redirected. For example\n            including http://monkey.com/survey1?c={{reply.observation.dyad.user.username}}\n            would pass the username of the study participant to the external system.\n            In contrast including {{reply.observation.id}} would simply pass the\n            anonymous Observation id number. Where a questionnaire will be\n            completed more than once during the study, it iss recommended to\n            include the {{reply.id}} or {{reply.token}} to allow for reconciling\n            external data with internal data at a later date.', null=True, verbose_name=b'Externally hosted questionnaire url', blank=True)),
                ('label', models.CharField(default=b'{{script.name}}', help_text='<p>This field allows individual observations to have a\n        meaningful label when listed for participants.  Either enter a simple\n        text string, for example "Main questionnaire", or have the label created\n        dynamically from information about this script object.</p>\n<p>For example, you can enter <code>{{i}}</code> to add the index in of a particular\nobservation in a sequence  of generated observations. If you enter <code>{{n}}</code>\nthen this will be the position (\'first\', \'second\' etc.).</p>\n<p>Advanced use: If you want to reference attributes of the Script or Membership\nobjects these are passed in as extra context, so {{script.name}}\nincludes the script name, and <code>{{membership.user.last_name}}</code> would\ninclude the user\'s surname. Mistakes when entering  these variable names\nwill not result in an error, but won\'t produce any output either. </p>', max_length=255, blank=True)),
                ('script_subject', models.CharField(help_text=b'Subject line of an email if required. Can use django\n        template syntax to include variables: {{var}}. Currently variables\n        available are {{url}} (the link to the questionnaire), {{user}} and\n        {{userprofile}} and {{observation}}.', max_length=1024, verbose_name=b'Email subject', blank=True)),
                ('script_body', models.TextField(help_text=b"Used for Email or SMS body. Can use django template syntax\n        to include variables: {{var}}. Currently variables available are {{url}}\n        (the link to the questionnaire), {{user}} and {{userprofile}} and\n        {{observation}}. Note that these are references to the django objects\n        themselves, so you can use the dot notation to access other attributed.\n        {{user.email}} or {{user.last_name}} for example, would print the user's\n        email address or last name.", verbose_name=b'Message', blank=True)),
                ('user_instructions', models.TextField(help_text=b'Instructions shown to user on their homepage and perhaps\n        elsewhere as the link to the survey. For example, "Please fill in the\n        questionnaire above. You will need to allow N minutes to do this  in\n        full." ', null=True, blank=True)),
                ('max_number_observations', models.IntegerField(default=1, help_text=b'The # of observations this scipt will generate.\n            Default is 1', verbose_name=b'create N observations')),
                ('repeat', models.CharField(default=b'DAILY', max_length=80, choices=[(b'YEARLY', b'YEARLY'), (b'MONTHLY', b'MONTHLY'), (b'WEEKLY', b'WEEKLY'), (b'DAILY', b'DAILY'), (b'HOURLY', b'HOURLY'), (b'MINUTELY', b'MINUTELY'), (b'SECONDLY', b'SECONDLY')])),
                ('repeat_from', models.DateTimeField(help_text=b'Leave blank for the observations to start relative to the\n        datetime they are  created (i.e. when the participant is randomised)', null=True, verbose_name=b'Fixed start date', blank=True)),
                ('repeat_interval', models.IntegerField(help_text=b'The interval between each freq iteration. For example,\n        when repeating WEEKLY, an interval of 2 means once per fortnight,\n        but with HOURLY, it means once every two hours.', null=True, verbose_name=b'repeat interval', blank=True)),
                ('repeat_byhours', models.CommaSeparatedIntegerField(validators=[signalbox.models.validators.valid_hours_list], max_length=20, blank=True, help_text=b"A number or list of integers, indicating the hours of the\n       day at which observations are made. For example, '13,19' would make\n       observations happen at 1pm and 7pm.", null=True, verbose_name=b'repeat at these hours')),
                ('repeat_byminutes', models.CommaSeparatedIntegerField(validators=[signalbox.models.validators.in_minute_range], max_length=20, blank=True, help_text=b'A list of numbers indicating at what minutes past the\n        hour the observations should be created. E.g. 0,30 will create\n        observations on the hour and half hour', null=True, verbose_name=b'repeat at these minutes past the hour')),
                ('repeat_bydays', models.CharField(help_text=b'One or more of MO, TU, WE, TH, FR, SA, SU separated by a\n        comma, to indicate which days observations will be created on.', max_length=100, null=True, verbose_name=b'repeat on these days of the week', blank=True)),
                ('repeat_bymonths', models.CommaSeparatedIntegerField(help_text=b"A comma separated list of months as numbers (1-12),\n        indicating the months in which obervations can be made. E.g. '1,6' would\n        mean observations are only made in Jan and June.", max_length=20, null=True, verbose_name=b'repeat in these months', blank=True)),
                ('repeat_bymonthdays', models.CommaSeparatedIntegerField(help_text=b"An integer or comma separated list of integers; represents\n        days within a  month on observations are created. For example, '1, 24'\n        would create observations on the first and 24th of each month.", max_length=20, null=True, verbose_name=b'on these days in the month', blank=True)),
                ('delay_by_minutes', models.IntegerField(default=0, help_text=b'Start the\n        observations this many minutes from the time the Observations are added.')),
                ('delay_by_hours', models.IntegerField(default=0, help_text=b'Start the\n        observations this many hours from the time the Observations are added.')),
                ('delay_by_days', models.IntegerField(default=0, help_text=b'Start the\n        observations this many days from the time the Observations are added.')),
                ('delay_by_weeks', models.IntegerField(default=0, help_text=b'Start the\n        observations this many weeks from the time the Observations are added.', null=True)),
                ('delay_in_whole_days_only', models.BooleanField(default=True, help_text=b'If true, observations are delayed to the nearest number of\n        whole days, and repeat rules will start from 00:00 on the morning of\n        that day.')),
                ('natural_date_syntax', models.TextField(blank=True, help_text='<p>Each line in this field will be read as a date on which to make an observation\nwhen the script is executed. By default each date is created relative to the\ncurrent date and time at midnight. For example, if a user signed up when this\npage loaded, these lines:</p>\n<p><code>now</code>, <code>next week</code>, and <code>in 3 days at 5pm</code>\nwould create the following dates: <div id="exampletimes">.</div></p>\n<p><input type=hidden id="examplesyntax" value="now \n next week \n in 3 days at 5pm">\n<script type="text/javascript">\n$.post("/admin/signalbox/preview/timings/",\n    {\'syntax\': $(\'#examplesyntax\').val() },\n    function(data) { $(\'#exampletimes\').html(data);}\n);\n</script></p>\n<div class="alert">\n<i class="icon-warning-sign"></i>\nNote that specifying options here will override other\nadvanced timing options specified in other panels.</div>\n\n<p><a class="btn timingsdetail" href="#"\n    onclick="$(\'.timingsdetail\').toggle();return false;">Show more examples</a></p>\n<div class="hide timingsdetail">\n\nOther examples include:\n\n<pre>\n    3 days from now\n    a day ago\n    in 2 weeks\n    in 3 days at 5pm\n    now\n    10 minutes ago\n    10 minutes from now\n    in 10 minutes\n    in a minute\n    in 30 seconds\n    tomorrow at noon\n    tomorrow at 6am\n    today at 12:15 AM\n    2 days from today at 2pm\n    a week from today\n    a week from now\n    3 weeks ago\n    next Sunday at noon\n    Sunday noon\n    next Sunday at 2pm\n</pre>\n\nHOWEVER - you must check the times have been interpreted properly before using\nthe script.\n</div>', null=True, validators=[signalbox.models.validators.valid_natural_datetime])),
                ('completion_window', models.IntegerField(help_text=b'Window in minutes during which the observation can be\n        completed. If left blank, the observation will not expire.', null=True, blank=True)),
                ('jitter', models.IntegerField(help_text=b'Number of minutes (plus or minus) to randomise observation\n        timing by.', null=True, blank=True)),
                ('asker', models.ForeignKey(blank=True, to='ask.Asker', help_text=b'Survey which the participant will complete for the\n        Observations created by this script', null=True, verbose_name=b'Attached questionnaire')),
            ],
            options={
                'ordering': ['reference', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScriptReminder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hours_delay', models.PositiveIntegerField(default=b'48')),
                ('reminder', models.ForeignKey(to='signalbox.Reminder')),
                ('script', models.ForeignKey(to='signalbox.Script')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScriptType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('observation_subclass_name', models.CharField(max_length=255, blank=True)),
                ('require_study_ivr_number', models.BooleanField(default=False)),
                ('sends_message_to_user', models.BooleanField(default=True, help_text=b'True\n        if observations created with this type of script send some form of\n        message to a user (e.g. email, sms or phone calls).')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auto_randomise', models.BooleanField(default=True, help_text=b'If on, then users are automatically added to a study\n            condition when a new membership is created.')),
                ('auto_add_observations', models.BooleanField(default=True, help_text=b'If on, and auto_randomise is also on, then observations will\n            be created when a membership is created. Has no effect if\n            auto_randomise is off.')),
                ('visible', models.BooleanField(default=False, help_text=b'Controls the display of the study on the /studies/ page.', db_index=True)),
                ('paused', models.BooleanField(default=False, help_text=b'If True, pauses sending of signals. Observations missed\n        will not be caught up later without manual intervention.', db_index=True)),
                ('slug', models.SlugField(help_text=b'A short name\n        used to refer to the study in URLs and other places.')),
                ('name', models.CharField(max_length=200)),
                ('study_email', models.EmailField(help_text=b'The return email address for all mailings/alerts.', max_length=75)),
                ('blurb', models.TextField(help_text=b'Snippet of\n        information displayed on the studies listing page.', null=True, blank=True)),
                ('study_image', models.ImageField(storage=signalbox.s3.CustomS3BotoStorage(), null=True, upload_to=b'study/images/', blank=True)),
                ('briefing', models.TextField(help_text=b'Key information displayed to participants before joining\n        the study.', null=True, blank=True)),
                ('consent_text', models.TextField(help_text=b'User must agree to this before entering study.', null=True, blank=True)),
                ('welcome_text', models.TextField(default=b'Welcome to the study', help_text=b'Text user sees in a message box when they signup for the\n        the study. Note his message is not needed if participants will be\n        added to studies by the experimenter, rather than through the\n        website.', null=True, blank=True)),
                ('max_redial_attempts', models.IntegerField(default=3, help_text=b'Only relevant for telephone calls: maximium\n        number of times to try and complete the call. Default\n        if nothing is specified is 3')),
                ('redial_delay', models.IntegerField(default=30, help_text=b'Number of minutes to wait before calling again (mainly for phone calls)')),
                ('working_day_starts', models.PositiveIntegerField(default=8, help_text=b'Hour (24h clock) at which phone\n            calls and texts should start to be made', validators=[signalbox.models.validators.is_24_hour])),
                ('working_day_ends', models.PositiveIntegerField(default=22, help_text=b'Hour (24h clock) at which phone\n            calls and texts should stop.', validators=[signalbox.models.validators.is_24_hour])),
                ('show_study_condition_to_user', models.BooleanField(default=False, help_text=b'If True, the user will be able to see their condition on\n        their homepage. Useful primarily for experiments where participants\n        signs up with the experimenter present and where blinding is not a\n        concern (e.g. where the experimenter carries out one of several\n        manipulations).')),
                ('randomisation_probability', models.DecimalField(default=0.5, help_text=b'Indicates the probability that the adaptive algorithm will\n        choose weighted randomisation rather than allocation to the group which\n        minimises the imbalance (minimisation or adaptive randomisation).\n        For example, if set to .5, then deterministic allocation to the\n        smallest group will only happen half of the time. To turn off adaptive\n        randomisation set to 1.', max_digits=2, decimal_places=1)),
                ('visible_profile_fields', models.CharField(blank=True, max_length=200, null=True, help_text=b'Available profile fields\n        for this study. Can be any of: landline, mobile, site, address_1, address_2, address_3, county, postcode, separated by a space.', validators=[signalbox.models.validators.only_includes_allowed_fields])),
                ('required_profile_fields', models.CharField(blank=True, max_length=200, null=True, help_text=b'Profile fields which users\n        will be forced to complete for this study. Can be any of: landline, mobile, site, address_1, address_2, address_3, county, postcode,\n        separated by a space.', validators=[signalbox.models.validators.only_includes_allowed_fields])),
                ('valid_telephone_country_codes', models.CommaSeparatedIntegerField(default=b'44', help_text=b'Valid national dialing codes for participants in this study.', max_length=32)),
                ('ad_hoc_askers', models.ManyToManyField(help_text=b'Questionnaires which can be completed ad-hoc.', to='ask.Asker', null=True, verbose_name=b'Questionnaires available ad-hoc', blank=True)),
                ('ad_hoc_scripts', models.ManyToManyField(help_text=b"Scripts which can be initiated by users on an ad-hoc basis.\n        IMPORTANT. Scripts selected here will appear on the 'add extra data' tab\n        of participants' profile pages, and will display the name of the study,\n        and the name of the script along with the username of any related\n        membership. BE SURE THESE DO NOT LEAK INFORMATION you would not which\n        participants to see.", to='signalbox.Script', null=True, verbose_name=b'scripts allowed on an ad-hoc basis', blank=True)),
                ('createifs', models.ManyToManyField(help_text=b'Rules by which new observations might be made in response\n        to participant answers.', to='signalbox.ObservationCreator', null=True, verbose_name=b'Rules to create new\n        observations based on user responses', blank=True)),
                ('participants', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='signalbox.Membership')),
                ('twilio_number', models.ForeignKey(blank=True, to='twiliobox.TwilioNumber', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'studies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudyCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.SlugField(default=b'main', max_length=255)),
                ('display_name', models.CharField(help_text=b'A label for this condition which can be shown to\n        the Participant (e.g. a non-descriptive name used to identify a\n        condition in an experimental session without breaking a blind.', max_length=30, null=True, blank=True)),
                ('weight', models.IntegerField(default=1, help_text=b'Relative weights to allocate users to conditions')),
                ('scripts', models.ManyToManyField(to='signalbox.Script', null=True, blank=True)),
                ('study', models.ForeignKey(blank=True, to='signalbox.Study', null=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='signalbox.Membership')),
            ],
            options={
                'ordering': ['study', 'tag'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudySite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b"e.g. 'Liverpool', 'London' ", max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextMessageCallback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sid', models.CharField(max_length=255)),
                ('post', jsonfield.fields.JSONField(help_text=b'A serialised\n        request.POST object from the twilio callback', null=True, blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=255, null=True, blank=True)),
                ('likely_related_user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_type', models.CharField(default=(b'Email', b'Email'), max_length=80, verbose_name=b'Send as', choices=[(b'Email', b'Email'), (b'SMS', b'SMS')])),
                ('subject', models.CharField(max_length=200, null=True, blank=True)),
                ('message', models.TextField(blank=True)),
                ('state', django_fsm.db.fields.fsmfield.FSMField(default=b'pending', max_length=50)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('message_from', models.ForeignKey(related_name=b'from', to=settings.AUTH_USER_MODEL)),
                ('message_to', models.ForeignKey(related_name=b'to', verbose_name=b'To', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_modified'],
                'permissions': (('can_send_message', 'Can send email/SMS to participant.'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', shortuuidfield.fields.ShortUUIDField(max_length=22, editable=False, blank=True)),
                ('landline', signalbox.phone_field.PhoneNumberField(blank=True, max_length=16, null=True, validators=[signalbox.models.validators.is_number_from_study_area, signalbox.models.validators.is_landline])),
                ('mobile', signalbox.phone_field.PhoneNumberField(validators=[signalbox.models.validators.is_number_from_study_area], max_length=16, blank=True, help_text=b'mobile phone number, with international prefix', null=True, verbose_name=b'Mobile telephone number')),
                ('prefer_mobile', models.BooleanField(default=True, help_text=b'Make calls to mobile telephone number where possible. Unticking this\n        means the user prefers calls on their landline.')),
                ('address_1', models.CharField(max_length=200, null=True, blank=True)),
                ('address_2', models.CharField(max_length=200, null=True, blank=True)),
                ('address_3', models.CharField(max_length=200, null=True, blank=True)),
                ('postcode', models.CharField(help_text=b'This is the postcode of your current address.', max_length=10, null=True, blank=True)),
                ('county', models.CharField(max_length=50, null=True, blank=True)),
                ('title', models.CharField(blank=True, max_length=20, null=True, choices=[(b'', b''), (b'Mr', b'Mr'), (b'Mrs', b'Mrs'), (b'Ms', b'Ms'), (b'Miss', b'Miss'), (b'Dr', b'Dr'), (b'Prof', b'Prof'), (b'Rev', b'Rev')])),
                ('professional_registration_number', models.CharField(help_text=b'A registration number for health professionals.', max_length=200, null=True, blank=True)),
                ('organisation', models.CharField(help_text=b'e.g. the\n        name of the surgery or hospital to which you are attached', max_length=200, null=True, blank=True)),
                ('site', models.ForeignKey(blank=True, to='signalbox.StudySite', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='script',
            name='reminders',
            field=models.ManyToManyField(to='signalbox.Reminder', through='signalbox.ScriptReminder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='script',
            name='script_type',
            field=models.ForeignKey(help_text=b'IMPORTANT: This type attribute determines the\n        interpretation of some fields below.', to='signalbox.ScriptType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observationcreator',
            name='script',
            field=models.ForeignKey(to='signalbox.Script'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observationcreator',
            name='showif',
            field=models.ForeignKey(to='ask.ShowIf'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='created_by_script',
            field=models.ForeignKey(blank=True, editable=False, to='signalbox.Script', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='dyad',
            field=models.ForeignKey(blank=True, to='signalbox.Membership', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='condition',
            field=models.ForeignKey(blank=True, to='signalbox.StudyCondition', help_text=b'Choose a Study/Condition for this user. To use Randomisation you must\n        save the Membership first, then randomise to a condition using the tools menu (or\n        if set, the study may auto-randomise the participant).', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='relates_to',
            field=models.ForeignKey(related_name=b'membership_relates_to', blank=True, to='signalbox.Membership', help_text=b'Sometimes a researcher may themselves become a subject in a study (for\n        example to provide ratings of different patients progress). In this instance they may\n        be added to the study multiple times, with the relates_to field set to another User,\n        for which they are providing data.', null=True, verbose_name=b'Linked patient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='study',
            field=models.ForeignKey(to='signalbox.Study'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(help_text=b'The person providing data, normally the participant.', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='reply',
            field=models.ForeignKey(blank=True, to='signalbox.Reply', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('question', 'reply', 'page'), ('other_variable_name', 'reply', 'page')]),
        ),
        migrations.AddField(
            model_name='alertinstance',
            name='reply',
            field=models.ForeignKey(to='signalbox.Reply'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='alert',
            name='study',
            field=models.ForeignKey(to='signalbox.Study'),
            preserve_default=True,
        ),
    ]
