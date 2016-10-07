# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shortuuidfield.fields
import yamlfield.fields
import ask.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ask', '0003_asker_width'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asker',
            name='finish_on_last_page',
            field=models.BooleanField(default=False, help_text='Mark the reply as complete\n        when the user gets to the last page. NOTE this implies there should be not questions\n        requiring input on the last page, or these values will never be saved.'),
        ),
        migrations.AlterField(
            model_name='asker',
            name='redirect_url',
            field=models.CharField(default='/profile/', max_length=128, help_text='"URL to redirect to when Questionnaire is complete.'),
        ),
        migrations.AlterField(
            model_name='asker',
            name='show_progress',
            field=models.BooleanField(default=False, help_text='Show a\n            progress field in the header of each page.'),
        ),
        migrations.AlterField(
            model_name='asker',
            name='slug',
            field=models.SlugField(verbose_name='Reference code', unique=True, max_length=128, help_text='To use in URLs etc'),
        ),
        migrations.AlterField(
            model_name='asker',
            name='step_navigation',
            field=models.BooleanField(default=True, help_text='Allow navigation\n        to steps.'),
        ),
        migrations.AlterField(
            model_name='asker',
            name='steps_are_sequential',
            field=models.BooleanField(default=True, help_text="Each page\n        in the questionnaire must be completed before the next; if unchecked\n        then respondents can skip around within the questionnaire and complete\n        the pages 'out of order'."),
        ),
        migrations.AlterField(
            model_name='asker',
            name='success_message',
            field=models.TextField(default='Questionnaire complete.', help_text='Message which appears in banner on users screen on completion of the  questionnaire.'),
        ),
        migrations.AlterField(
            model_name='asker',
            name='system_audio',
            field=yamlfield.fields.YAMLField(blank=True, help_text='A mapping of slugs to text strings or\n        urls which store audio files, for the system to play on errors etc. during IVR calls'),
        ),
        migrations.AlterField(
            model_name='askpage',
            name='submit_button_text',
            field=models.CharField(default='Continue', max_length=255),
        ),
        migrations.AlterField(
            model_name='choice',
            name='is_default_value',
            field=models.BooleanField(db_index=True, default=False, help_text='Indicates whether the value will be checked by default.'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='mapped_score',
            field=models.IntegerField(blank=True, null=True, help_text='The value to be used when computing scoresheets. Does not affect what is stored or exported.'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='order',
            field=models.IntegerField(db_index=True, help_text='Order in which the choices are displayed.'),
        ),
        migrations.AlterField(
            model_name='choice',
            name='score',
            field=models.IntegerField(help_text='This is the value saved in the DB'),
        ),
        migrations.AlterField(
            model_name='choiceset',
            name='yaml',
            field=yamlfield.fields.YAMLField(blank=True, validators=[ask.validators.checkyamlchoiceset], default="\n1:\n  label: 'One'\n  score: 1\n2:\n  is_default_value: true\n  label: 'Two'\n  score: 2\n3:\n  label: 'More than two'\n  score: 2\n    "),
        ),
        migrations.AlterField(
            model_name='question',
            name='extra_attrs',
            field=yamlfield.fields.YAMLField(blank=True, help_text='A YAML representation of a python dictionary of\n        attributes which, when deserialised, is passed to the form widget when the questionnaire is\n        rendered. See django-floppyforms docs for options.'),
        ),
        migrations.AlterField(
            model_name='question',
            name='order',
            field=models.IntegerField(verbose_name='Page order', default=-1, help_text='The order in which items will apear in the page.'),
        ),
        migrations.AlterField(
            model_name='question',
            name='q_type',
            field=models.CharField(default='instruction', max_length=100, choices=[('instruction', 'instruction'), ('likert', 'likert'), ('likert-list', 'likert-list'), ('pulldown', 'pulldown'), ('required-checkbox', 'required-checkbox'), ('checkboxes', 'checkboxes'), ('long-text', 'long-text'), ('open', 'open'), ('short-text', 'short-text'), ('integer', 'integer'), ('decimal', 'decimal'), ('slider', 'slider'), ('range-slider', 'range-slider'), ('date', 'date'), ('date-time', 'date-time'), ('time', 'time'), ('hangup', 'hangup'), ('upload', 'upload'), ('webcam', 'webcam')]),
        ),
        migrations.AlterField(
            model_name='question',
            name='variable_name',
            field=models.SlugField(max_length=32, help_text='Variable names can use characters a-Z,\n            0-9 and underscore (_), and must be unique within the system.', unique=True, default='', validators=[ask.validators.first_char_is_alpha, ask.validators.illegal_characters, ask.validators.is_lower]),
        ),
        migrations.AlterField(
            model_name='questionasset',
            name='asset',
            field=models.FileField(blank=True, null=True, upload_to='questionassets', help_text='Can be an image (.jpg, .png, or .gif), audio file (.m4a, .mp4, or .mp3) or\n        movie (.mp4 only) for display as part of the question text.'),
        ),
        migrations.AlterField(
            model_name='questionasset',
            name='slug',
            field=models.SlugField(help_text='A name to refer to this asset\n        with in the question_text field. To display an image or media\n        player within the question, include the text {{SLUG}} in the\n        question_text field of the question.'),
        ),
        migrations.AlterField(
            model_name='questionasset',
            name='template',
            field=models.CharField(max_length=255, choices=[('image.html', 'image'), ('movie.html', 'movie'), ('audio.html', 'audio')]),
        ),
        migrations.AlterField(
            model_name='showif',
            name='less_than',
            field=models.IntegerField(blank=True, null=True, help_text='Previous question response\n        or summary score must be less than this value.'),
        ),
        migrations.AlterField(
            model_name='showif',
            name='more_than',
            field=models.IntegerField(blank=True, null=True, help_text='Previous question response\n        or summary score must be more than this value.'),
        ),
        migrations.AlterField(
            model_name='showif',
            name='previous_question',
            field=models.ForeignKey(blank=True, help_text='For previous values, enter the name of the question which\n        will already have been answered in this survey (technically, within this Reply)', null=True, related_name='previous_question', to='ask.Question'),
        ),
        migrations.AlterField(
            model_name='showif',
            name='summary_score',
            field=models.ForeignKey(blank=True, help_text='A summary score to be calculated based on answer already entered in the current\n        Reply.', null=True, to='signalbox.ScoreSheet'),
        ),
        migrations.AlterField(
            model_name='showif',
            name='values',
            field=models.CharField(blank=True, null=True, max_length=255, help_text='CASE INSENSITIVE values to match, comma separated. The question is shown if\n        any value matches'),
        )
    ]
