# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ChoiceSet.yaml'
        db.add_column(u'ask_choiceset', 'yaml',
                      self.gf('yamlfield.fields.YAMLField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ChoiceSet.yaml'
        db.delete_column(u'ask_choiceset', 'yaml')


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