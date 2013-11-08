# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'QuestionAsset'
        db.create_table(u'ask_questionasset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.Question'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('asset', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('ask', ['QuestionAsset'])

        # Adding model 'Question'
        db.create_table(u'ask_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.AskPage'], null=True, blank=True)),
            ('instrument', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.Instrument'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('allow_not_applicable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('showif', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.ShowIf'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('variable_name', self.gf('django.db.models.fields.SlugField')(default='', unique=True, max_length=32)),
            ('choiceset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.ChoiceSet'], null=True, blank=True)),
            ('display_instrument', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='display_instrument', null=True, to=orm['ask.Instrument'])),
            ('score_mapping', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('audio', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('q_type', self.gf('django.db.models.fields.CharField')(default='instruction', max_length=100)),
            ('widget_kwargs', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
            ('field_kwargs', self.gf('jsonfield.fields.JSONField')(default={}, blank=True)),
        ))
        db.send_create_signal('ask', ['Question'])

        # Adding model 'Choice'
        db.create_table(u'ask_choice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choiceset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.ChoiceSet'], null=True, blank=True)),
            ('is_default_value', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('ask', ['Choice'])

        # Adding unique constraint on 'Choice', fields ['choiceset', 'score']
        db.create_unique(u'ask_choice', ['choiceset_id', 'score'])

        # Adding model 'ChoiceSet'
        db.create_table(u'ask_choiceset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
        ))
        db.send_create_signal('ask', ['ChoiceSet'])

        # Adding model 'ShowIf'
        db.create_table(u'ask_showif', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('previous_question', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='previous_question', null=True, to=orm['ask.Question'])),
            ('summary_score', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['signalbox.ScoreSheet'], null=True, blank=True)),
            ('values', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('more_than', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('less_than', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('ask', ['ShowIf'])

        # Adding model 'Instrument'
        db.create_table(u'ask_instrument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('citation', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('usage_information', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('ask', ['Instrument'])

        # Adding unique constraint on 'Instrument', fields ['name']
        db.create_unique(u'ask_instrument', ['name'])

        # Adding model 'AskPage'
        db.create_table(u'ask_askpage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ask.Asker'])),
            ('order', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('submit_button_text', self.gf('django.db.models.fields.CharField')(default='Continue', max_length=255)),
            ('step_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('ask', ['AskPage'])

        # Adding unique constraint on 'AskPage', fields ['order', 'asker']
        db.create_unique(u'ask_askpage', ['order', 'asker_id'])

        # Adding model 'Asker'
        db.create_table(u'ask_asker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128)),
            ('success_message', self.gf('django.db.models.fields.TextField')(default='Questionnaire complete.')),
            ('redirect_url', self.gf('django.db.models.fields.CharField')(default='/accounts/profile/', max_length=128)),
            ('show_progress', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('step_navigation', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('steps_are_sequential', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('hide_menu', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('ask', ['Asker'])

        # Adding M2M table for field scoresheets on 'Asker'
        m2m_table_name = db.shorten_name(u'ask_asker_scoresheets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('asker', models.ForeignKey(orm['ask.asker'], null=False)),
            ('scoresheet', models.ForeignKey(orm['signalbox.scoresheet'], null=False))
        ))
        db.create_unique(m2m_table_name, ['asker_id', 'scoresheet_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'AskPage', fields ['order', 'asker']
        db.delete_unique(u'ask_askpage', ['order', 'asker_id'])

        # Removing unique constraint on 'Instrument', fields ['name']
        db.delete_unique(u'ask_instrument', ['name'])

        # Removing unique constraint on 'Choice', fields ['choiceset', 'score']
        db.delete_unique(u'ask_choice', ['choiceset_id', 'score'])

        # Deleting model 'QuestionAsset'
        db.delete_table(u'ask_questionasset')

        # Deleting model 'Question'
        db.delete_table(u'ask_question')

        # Deleting model 'Choice'
        db.delete_table(u'ask_choice')

        # Deleting model 'ChoiceSet'
        db.delete_table(u'ask_choiceset')

        # Deleting model 'ShowIf'
        db.delete_table(u'ask_showif')

        # Deleting model 'Instrument'
        db.delete_table(u'ask_instrument')

        # Deleting model 'AskPage'
        db.delete_table(u'ask_askpage')

        # Deleting model 'Asker'
        db.delete_table(u'ask_asker')

        # Removing M2M table for field scoresheets on 'Asker'
        db.delete_table(db.shorten_name(u'ask_asker_scoresheets'))


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
        'ask.choice': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('choiceset', 'score'),)", 'object_name': 'Choice'},
            'choiceset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.ChoiceSet']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default_value': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {})
        },
        'ask.choiceset': {
            'Meta': {'ordering': "['name']", 'object_name': 'ChoiceSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'})
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
        'ask.questionasset': {
            'Meta': {'object_name': 'QuestionAsset'},
            'asset': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ask.Question']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
        'signalbox.scoresheet': {
            'Meta': {'object_name': 'ScoreSheet'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'function': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minimum_number_of_responses_required': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'variables': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'varsinscoresheet'", 'symmetrical': 'False', 'to': "orm['ask.Question']"})
        }
    }

    complete_apps = ['ask']