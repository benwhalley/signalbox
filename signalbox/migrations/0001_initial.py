# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ScoreSheet'
        db.create_table(u'signalbox_scoresheet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('minimum_number_of_responses_required', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('function', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('signalbox', ['ScoreSheet'])

        # Adding M2M table for field variables on 'ScoreSheet'
        m2m_table_name = db.shorten_name(u'signalbox_scoresheet_variables')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('scoresheet', models.ForeignKey(orm['signalbox.scoresheet'], null=False)),
            ('question', models.ForeignKey(orm['ask.question'], null=False))
        ))
        db.create_unique(m2m_table_name, ['scoresheet_id', 'question_id'])

        # Adding model 'Answer'
        db.create_table(u'signalbox_answer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.Question'], null=True, on_delete=models.PROTECT, blank=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.AskPage'], null=True, on_delete=models.PROTECT, blank=True)),
            ('other_variable_name', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('choices', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('answer', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('upload', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('reply', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Reply'], null=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('meta', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'signalbox', ['Answer'])

        # Adding unique constraint on 'Answer', fields ['other_variable_name', 'reply', 'page']
        db.create_unique(u'signalbox_answer', ['other_variable_name', 'reply_id', 'page_id'])

        # Adding unique constraint on 'Answer', fields ['question', 'reply', 'page']
        db.create_unique(u'signalbox_answer', ['question_id', 'reply_id', 'page_id'])

        # Adding model 'Reply'
        db.create_table(u'signalbox_reply', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_canonical_reply', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('observation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Observation'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reply_user', null=True, to=orm['auth.User'])),
            ('asker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.Asker'], null=True, blank=True)),
            ('redirect_to', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('last_submit', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('originally_collected_on', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('complete', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('twilio_question_index', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('entry_method', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('collector', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['Reply'])

        # Adding model 'ScriptType'
        db.create_table(u'signalbox_scripttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('observation_subclass_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('require_study_ivr_number', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sends_message_to_user', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('signalbox', ['ScriptType'])

        # Adding model 'Reminder'
        db.create_table(u'signalbox_reminder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('kind', self.gf('django.db.models.fields.CharField')(default='email', max_length=100)),
            ('from_address', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('signalbox', ['Reminder'])

        # Adding model 'ScriptReminder'
        db.create_table(u'signalbox_scriptreminder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hours_delay', self.gf('django.db.models.fields.PositiveIntegerField')(default='48')),
            ('script', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Script'])),
            ('reminder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Reminder'])),
        ))
        db.send_create_signal('signalbox', ['ScriptReminder'])

        # Adding model 'Script'
        db.create_table(u'signalbox_script', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True)),
            ('is_clinical_data', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('breaks_blind', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_in_tasklist', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_display_of_results', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_replies_on_dashboard', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('script_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.ScriptType'])),
            ('asker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.Asker'], null=True, blank=True)),
            ('external_asker_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(default='{{script.name}}', max_length=255, blank=True)),
            ('script_subject', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('script_body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user_instructions', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('max_number_observations', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('repeat', self.gf('django.db.models.fields.CharField')(default='DAILY', max_length=80)),
            ('repeat_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('repeat_interval', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('repeat_byhours', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=20, null=True, blank=True)),
            ('repeat_byminutes', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=20, null=True, blank=True)),
            ('repeat_bydays', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('repeat_bymonths', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=20, null=True, blank=True)),
            ('repeat_bymonthdays', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=20, null=True, blank=True)),
            ('delay_by_minutes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('delay_by_hours', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('delay_by_days', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('delay_by_weeks', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
            ('delay_in_whole_days_only', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('natural_date_syntax', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('completion_window', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('jitter', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['Script'])

        # Adding model 'ReminderInstance'
        db.create_table(u'signalbox_reminderinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reminder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Reminder'])),
            ('observation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Observation'])),
            ('due', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('signalbox', ['ReminderInstance'])

        # Adding model 'Observation'
        db.create_table(u'signalbox_observation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('n_in_sequence', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('dyad', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Membership'], null=True, blank=True)),
            ('created_by_script', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Script'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('due_original', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('due', self.gf('django.db.models.fields.DateTimeField')(null=True, db_index=True)),
            ('last_attempted', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('offset', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('attempt_count', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('n_questions', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('n_questions_incomplete', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['Observation'])

        # Adding model 'ObservationData'
        db.create_table(u'signalbox_observationdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('observation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Observation'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('value', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['ObservationData'])

        # Adding model 'TextMessageCallback'
        db.create_table(u'signalbox_textmessagecallback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('post', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('likely_related_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['TextMessageCallback'])

        # Adding model 'Membership'
        db.create_table(u'signalbox_membership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('study', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Study'])),
            ('relates_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='membership_relates_to', null=True, to=orm['signalbox.Membership'])),
            ('condition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.StudyCondition'], null=True, blank=True)),
            ('date_joined', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('date_randomised', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['Membership'])

        # Adding model 'StudySite'
        db.create_table(u'signalbox_studysite', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('signalbox', ['StudySite'])

        # Adding model 'Study'
        db.create_table(u'signalbox_study', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auto_randomise', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('auto_add_observations', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('paused', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('study_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('twilio_number', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['twiliobox.TwilioNumber'], null=True, blank=True)),
            ('blurb', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('study_image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('briefing', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('consent_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('welcome_text', self.gf('django.db.models.fields.TextField')(default='Welcome to the study', null=True, blank=True)),
            ('max_redial_attempts', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('redial_delay', self.gf('django.db.models.fields.IntegerField')(default=30)),
            ('working_day_starts', self.gf('django.db.models.fields.PositiveIntegerField')(default=8)),
            ('working_day_ends', self.gf('django.db.models.fields.PositiveIntegerField')(default=22)),
            ('show_study_condition_to_user', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allocation_method', self.gf('django.db.models.fields.CharField')(default='balanced_groups_adaptive_randomisation', max_length=85)),
            ('randomisation_probability', self.gf('django.db.models.fields.DecimalField')(default=0.5, null=True, max_digits=2, decimal_places=1, blank=True)),
            ('visible_profile_fields', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('required_profile_fields', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('valid_telephone_country_codes', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(default='44', max_length=32)),
        ))
        db.send_create_signal('signalbox', ['Study'])

        # Adding M2M table for field ad_hoc_scripts on 'Study'
        m2m_table_name = db.shorten_name(u'signalbox_study_ad_hoc_scripts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('study', models.ForeignKey(orm['signalbox.study'], null=False)),
            ('script', models.ForeignKey(orm['signalbox.script'], null=False))
        ))
        db.create_unique(m2m_table_name, ['study_id', 'script_id'])

        # Adding M2M table for field createifs on 'Study'
        m2m_table_name = db.shorten_name(u'signalbox_study_createifs')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('study', models.ForeignKey(orm['signalbox.study'], null=False)),
            ('observationcreator', models.ForeignKey(orm['signalbox.observationcreator'], null=False))
        ))
        db.create_unique(m2m_table_name, ['study_id', 'observationcreator_id'])

        # Adding model 'StudyCondition'
        db.create_table(u'signalbox_studycondition', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('study', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Study'], null=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.SlugField')(default='main', max_length=255)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('signalbox', ['StudyCondition'])

        # Adding M2M table for field scripts on 'StudyCondition'
        m2m_table_name = db.shorten_name(u'signalbox_studycondition_scripts')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('studycondition', models.ForeignKey(orm['signalbox.studycondition'], null=False)),
            ('script', models.ForeignKey(orm['signalbox.script'], null=False))
        ))
        db.create_unique(m2m_table_name, ['studycondition_id', 'script_id'])

        # Adding model 'StudyPeriod'
        db.create_table(u'signalbox_studyperiod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('study', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Study'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('tag', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('start', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('end', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('signalbox', ['StudyPeriod'])

        # Adding model 'UserProfile'
        db.create_table(u'signalbox_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('landline', self.gf('signalbox.phone_field.PhoneNumberField')(max_length=16, null=True, blank=True)),
            ('mobile', self.gf('signalbox.phone_field.PhoneNumberField')(max_length=16, null=True, blank=True)),
            ('prefer_mobile', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('address_3', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('postcode', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('county', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.StudySite'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('professional_registration_number', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('organisation', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['UserProfile'])

        # Adding model 'Alert'
        db.create_table(u'signalbox_alert', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('study', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Study'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('mobile', self.gf('phonenumber_field.modelfields.PhoneNumberField')(max_length=128, null=True, blank=True)),
            ('condition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.ShowIf'])),
        ))
        db.send_create_signal('signalbox', ['Alert'])

        # Adding model 'AlertInstance'
        db.create_table(u'signalbox_alertinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('reply', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Reply'])),
            ('alert', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Alert'])),
            ('viewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('signalbox', ['AlertInstance'])

        # Adding model 'ObservationCreator'
        db.create_table(u'signalbox_observationcreator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('script', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.Script'])),
            ('showif', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.ShowIf'])),
        ))
        db.send_create_signal('signalbox', ['ObservationCreator'])

        # Adding model 'ContactReason'
        db.create_table(u'signalbox_contactreason', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('followup_expected', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('signalbox', ['ContactReason'])

        # Adding model 'ContactRecord'
        db.create_table(u'signalbox_contactrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('participant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('reason', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.ContactReason'], null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='added_by', to=orm['auth.User'])),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('signalbox', ['ContactRecord'])

        # Adding model 'UserMessage'
        db.create_table(u'signalbox_usermessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message_type', self.gf('django.db.models.fields.CharField')(default=('Email', 'Email'), max_length=80)),
            ('message_to', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to', to=orm['auth.User'])),
            ('message_from', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from', to=orm['auth.User'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('state', self.gf('django_fsm.db.fields.fsmfield.FSMField')(default='pending', max_length=50)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('signalbox', ['UserMessage'])


    def backwards(self, orm):
        # Removing unique constraint on 'Answer', fields ['question', 'reply', 'page']
        db.delete_unique(u'signalbox_answer', ['question_id', 'reply_id', 'page_id'])

        # Removing unique constraint on 'Answer', fields ['other_variable_name', 'reply', 'page']
        db.delete_unique(u'signalbox_answer', ['other_variable_name', 'reply_id', 'page_id'])

        # Deleting model 'ScoreSheet'
        db.delete_table(u'signalbox_scoresheet')

        # Removing M2M table for field variables on 'ScoreSheet'
        db.delete_table(db.shorten_name(u'signalbox_scoresheet_variables'))

        # Deleting model 'Answer'
        db.delete_table(u'signalbox_answer')

        # Deleting model 'Reply'
        db.delete_table(u'signalbox_reply')

        # Deleting model 'ScriptType'
        db.delete_table(u'signalbox_scripttype')

        # Deleting model 'Reminder'
        db.delete_table(u'signalbox_reminder')

        # Deleting model 'ScriptReminder'
        db.delete_table(u'signalbox_scriptreminder')

        # Deleting model 'Script'
        db.delete_table(u'signalbox_script')

        # Deleting model 'ReminderInstance'
        db.delete_table(u'signalbox_reminderinstance')

        # Deleting model 'Observation'
        db.delete_table(u'signalbox_observation')

        # Deleting model 'ObservationData'
        db.delete_table(u'signalbox_observationdata')

        # Deleting model 'TextMessageCallback'
        db.delete_table(u'signalbox_textmessagecallback')

        # Deleting model 'Membership'
        db.delete_table(u'signalbox_membership')

        # Deleting model 'StudySite'
        db.delete_table(u'signalbox_studysite')

        # Deleting model 'Study'
        db.delete_table(u'signalbox_study')

        # Removing M2M table for field ad_hoc_scripts on 'Study'
        db.delete_table(db.shorten_name(u'signalbox_study_ad_hoc_scripts'))

        # Removing M2M table for field createifs on 'Study'
        db.delete_table(db.shorten_name(u'signalbox_study_createifs'))

        # Deleting model 'StudyCondition'
        db.delete_table(u'signalbox_studycondition')

        # Removing M2M table for field scripts on 'StudyCondition'
        db.delete_table(db.shorten_name(u'signalbox_studycondition_scripts'))

        # Deleting model 'StudyPeriod'
        db.delete_table(u'signalbox_studyperiod')

        # Deleting model 'UserProfile'
        db.delete_table(u'signalbox_userprofile')

        # Deleting model 'Alert'
        db.delete_table(u'signalbox_alert')

        # Deleting model 'AlertInstance'
        db.delete_table(u'signalbox_alertinstance')

        # Deleting model 'ObservationCreator'
        db.delete_table(u'signalbox_observationcreator')

        # Deleting model 'ContactReason'
        db.delete_table(u'signalbox_contactreason')

        # Deleting model 'ContactRecord'
        db.delete_table(u'signalbox_contactrecord')

        # Deleting model 'UserMessage'
        db.delete_table(u'signalbox_usermessage')


    models = {
        'ask.asker': {
            'Meta': {'object_name': 'Asker'},
            'hide_menu': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'default': "'/accounts/profile/'", 'max_length': '128'}),
            'scoresheets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['signalbox.ScoreSheet']", 'null': 'True', 'blank': 'True'}),
            'show_progress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128'}),
            'step_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'steps_are_sequential': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'success_message': ('django.db.models.fields.TextField', [], {'default': "'Questionnaire complete.'"})
        },
        'ask.askpage': {
            'Meta': {'ordering': "['order']", 'unique_together': "(['order', 'asker'],)", 'object_name': 'AskPage'},
            'asker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Asker']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'step_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'submit_button_text': ('django.db.models.fields.CharField', [], {'default': "'Continue'", 'max_length': '255'})
        },
        'ask.choiceset': {
            'Meta': {'ordering': "['name']", 'object_name': 'ChoiceSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'}),
            'yaml': ('yamlfield.fields.YAMLField', [], {})
        },
        'ask.instrument': {
            'Meta': {'ordering': "['name']", 'unique_together': "(['name'],)", 'object_name': 'Instrument'},
            'citation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'usage_information': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'ask.question': {
            'Meta': {'ordering': "['order']", 'object_name': 'Question'},
            'allow_not_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'audio': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'choiceset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.ChoiceSet']", 'null': 'True', 'blank': 'True'}),
            'display_instrument': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'display_instrument'", 'null': 'True', 'to': "orm['ask.Instrument']"}),
            'field_kwargs': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instrument': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Instrument']", 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.AskPage']", 'null': 'True', 'blank': 'True'}),
            'q_type': ('django.db.models.fields.CharField', [], {'default': "'instruction'", 'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'score_mapping': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'showif': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.ShowIf']", 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'variable_name': ('django.db.models.fields.SlugField', [], {'default': "''", 'unique': 'True', 'max_length': '32'}),
            'widget_kwargs': ('jsonfield.fields.JSONField', [], {'default': '{}', 'blank': 'True'})
        },
        'ask.showif': {
            'Meta': {'object_name': 'ShowIf'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'less_than': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'more_than': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'previous_question': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'previous_question'", 'null': 'True', 'to': "orm['ask.Question']"}),
            'summary_score': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.ScoreSheet']", 'null': 'True', 'blank': 'True'}),
            'values': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'ordering': "['username']", 'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'signalbox.alert': {
            'Meta': {'object_name': 'Alert'},
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.ShowIf']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Study']"})
        },
        'signalbox.alertinstance': {
            'Meta': {'object_name': 'AlertInstance'},
            'alert': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Alert']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Reply']"}),
            'viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'signalbox.answer': {
            'Meta': {'ordering': "[u'last_modified']", 'unique_together': "([u'other_variable_name', u'reply', u'page'], [u'question', u'reply', u'page'])", 'object_name': 'Answer'},
            'answer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'choices': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'other_variable_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.AskPage']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Question']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Reply']", 'null': 'True', 'blank': 'True'}),
            'upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'signalbox.contactreason': {
            'Meta': {'ordering': "['name']", 'object_name': 'ContactReason'},
            'followup_expected': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'signalbox.contactrecord': {
            'Meta': {'ordering': "['-added']", 'object_name': 'ContactRecord'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'added_by'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'participant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.ContactReason']", 'null': 'True', 'blank': 'True'})
        },
        'signalbox.membership': {
            'Meta': {'ordering': "['-date_randomised']", 'object_name': 'Membership'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'condition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.StudyCondition']", 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_randomised': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relates_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'membership_relates_to'", 'null': 'True', 'to': "orm['signalbox.Membership']"}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Study']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'signalbox.observation': {
            'Meta': {'ordering': "['due']", 'object_name': 'Observation'},
            'attempt_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'created_by_script': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Script']", 'null': 'True', 'blank': 'True'}),
            'due': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'due_original': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'dyad': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Membership']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'last_attempted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'n_in_sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_questions': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'n_questions_incomplete': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'offset': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        'signalbox.observationcreator': {
            'Meta': {'object_name': 'ObservationCreator'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Script']"}),
            'showif': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.ShowIf']"})
        },
        'signalbox.observationdata': {
            'Meta': {'object_name': 'ObservationData'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Observation']"}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'signalbox.reminder': {
            'Meta': {'object_name': 'Reminder'},
            'from_address': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '100'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'})
        },
        'signalbox.reminderinstance': {
            'Meta': {'object_name': 'ReminderInstance'},
            'due': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Observation']"}),
            'reminder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Reminder']"}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        'signalbox.reply': {
            'Meta': {'ordering': "['-started']", 'object_name': 'Reply'},
            'asker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Asker']", 'null': 'True', 'blank': 'True'}),
            'collector': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'entry_method': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_canonical_reply': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_submit': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Observation']", 'null': 'True', 'blank': 'True'}),
            'originally_collected_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'redirect_to': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'}),
            'twilio_question_index': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reply_user'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        'signalbox.scoresheet': {
            'Meta': {'object_name': 'ScoreSheet'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_number_of_responses_required': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'variables': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'varsinscoresheet'", 'symmetrical': 'False', 'to': "orm['ask.Question']"})
        },
        'signalbox.script': {
            'Meta': {'ordering': "['reference', 'name']", 'object_name': 'Script'},
            'allow_display_of_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'asker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Asker']", 'null': 'True', 'blank': 'True'}),
            'breaks_blind': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'completion_window': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'delay_by_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'delay_by_hours': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'delay_by_minutes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'delay_by_weeks': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'delay_in_whole_days_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'external_asker_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_clinical_data': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jitter': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "'{{script.name}}'", 'max_length': '255', 'blank': 'True'}),
            'max_number_observations': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'natural_date_syntax': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True'}),
            'reminders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['signalbox.Reminder']", 'through': "orm['signalbox.ScriptReminder']", 'symmetrical': 'False'}),
            'repeat': ('django.db.models.fields.CharField', [], {'default': "'DAILY'", 'max_length': '80'}),
            'repeat_bydays': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'repeat_byhours': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'repeat_byminutes': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'repeat_bymonthdays': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'repeat_bymonths': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'repeat_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'repeat_interval': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'script_body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'script_subject': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'script_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.ScriptType']"}),
            'show_in_tasklist': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_replies_on_dashboard': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user_instructions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'signalbox.scriptreminder': {
            'Meta': {'object_name': 'ScriptReminder'},
            'hours_delay': ('django.db.models.fields.PositiveIntegerField', [], {'default': "'48'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reminder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Reminder']"}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Script']"})
        },
        'signalbox.scripttype': {
            'Meta': {'object_name': 'ScriptType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'observation_subclass_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'require_study_ivr_number': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sends_message_to_user': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'signalbox.study': {
            'Meta': {'ordering': "['name']", 'object_name': 'Study'},
            'ad_hoc_scripts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['signalbox.Script']", 'null': 'True', 'blank': 'True'}),
            'allocation_method': ('django.db.models.fields.CharField', [], {'default': "'balanced_groups_adaptive_randomisation'", 'max_length': '85'}),
            'auto_add_observations': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'auto_randomise': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'blurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'briefing': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'consent_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'createifs': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['signalbox.ObservationCreator']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_redial_attempts': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'participants': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': "orm['signalbox.Membership']", 'symmetrical': 'False'}),
            'paused': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'randomisation_probability': ('django.db.models.fields.DecimalField', [], {'default': '0.5', 'null': 'True', 'max_digits': '2', 'decimal_places': '1', 'blank': 'True'}),
            'redial_delay': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'required_profile_fields': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'show_study_condition_to_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'study_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'study_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'twilio_number': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['twiliobox.TwilioNumber']", 'null': 'True', 'blank': 'True'}),
            'valid_telephone_country_codes': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'default': "'44'", 'max_length': '32'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'visible_profile_fields': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'welcome_text': ('django.db.models.fields.TextField', [], {'default': "'Welcome to the study'", 'null': 'True', 'blank': 'True'}),
            'working_day_ends': ('django.db.models.fields.PositiveIntegerField', [], {'default': '22'}),
            'working_day_starts': ('django.db.models.fields.PositiveIntegerField', [], {'default': '8'})
        },
        'signalbox.studycondition': {
            'Meta': {'ordering': "['study', 'tag']", 'object_name': 'StudyCondition'},
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scripts': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['signalbox.Script']", 'null': 'True', 'blank': 'True'}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Study']", 'null': 'True', 'blank': 'True'}),
            'tag': ('django.db.models.fields.SlugField', [], {'default': "'main'", 'max_length': '255'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': "orm['signalbox.Membership']", 'symmetrical': 'False'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'signalbox.studyperiod': {
            'Meta': {'ordering': "['study', 'start', '-end']", 'object_name': 'StudyPeriod'},
            'end': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'start': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.Study']"}),
            'tag': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'signalbox.studysite': {
            'Meta': {'object_name': 'StudySite'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'signalbox.textmessagecallback': {
            'Meta': {'object_name': 'TextMessageCallback'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likely_related_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'post': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'signalbox.usermessage': {
            'Meta': {'ordering': "['-last_modified']", 'object_name': 'UserMessage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'message_from': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from'", 'to': u"orm['auth.User']"}),
            'message_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to'", 'to': u"orm['auth.User']"}),
            'message_type': ('django.db.models.fields.CharField', [], {'default': "('Email', 'Email')", 'max_length': '80'}),
            'state': ('django_fsm.db.fields.fsmfield.FSMField', [], {'default': "'pending'", 'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'signalbox.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'address_3': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landline': ('signalbox.phone_field.PhoneNumberField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'mobile': ('signalbox.phone_field.PhoneNumberField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'prefer_mobile': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'professional_registration_number': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['signalbox.StudySite']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'blank': 'True'})
        },
        u'twiliobox.twilionumber': {
            'Meta': {'object_name': 'TwilioNumber'},
            'answerphone_script': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Asker']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default_account': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'twilio_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'twilio_token': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['signalbox']