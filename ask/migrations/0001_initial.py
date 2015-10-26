# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ask.validators
import signalbox.process
import yamlfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('signalbox', '0004_auto_20151026_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True)),
                ('slug', models.SlugField(help_text=b'To use in URLs etc', unique=True, max_length=128, verbose_name=b'Reference code')),
                ('success_message', models.TextField(default=b'Questionnaire complete.', help_text=b'Message which appears in banner on users screen on completion of the  questionnaire.')),
                ('redirect_url', models.CharField(default=b'/profile/', help_text=b'"URL to redirect to when Questionnaire is complete.', max_length=128)),
                ('show_progress', models.BooleanField(default=False, help_text=b'Show a\n            progress field in the header of each page.')),
                ('finish_on_last_page', models.BooleanField(default=False, help_text=b'Mark the reply as complete\n        when the user gets to the last page. NOTE this implies there should be not questions\n        requiring input on the last page, or these values will never be saved.')),
                ('step_navigation', models.BooleanField(default=True, help_text=b'Allow navigation\n        to steps.')),
                ('steps_are_sequential', models.BooleanField(default=True, help_text=b"Each page\n        in the questionnaire must be completed before the next; if unchecked\n        then respondents can skip around within the questionnaire and complete\n        the pages 'out of order'.")),
                ('hide_menu', models.BooleanField(default=True)),
                ('system_audio', yamlfield.fields.YAMLField(help_text=b'A mapping of slugs to text strings or\n        urls which store audio files, for the system to play on errors etc. during IVR calls', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Questionnaire',
                'permissions': (('can_preview', 'Can preview surveys'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AskPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.FloatField(default=0)),
                ('submit_button_text', models.CharField(default=b'Continue', max_length=255)),
                ('step_name', models.CharField(max_length=255, null=True, blank=True)),
                ('randomise_questions', models.BooleanField(default=False)),
                ('asker', models.ForeignKey(to='ask.Asker')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'Page',
            },
            bases=(models.Model, signalbox.process.Step),
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_default_value', models.BooleanField(default=False, help_text=b'Indicates whether the value will be checked by default.', db_index=True)),
                ('order', models.IntegerField(help_text=b'Order in which the choices are displayed.', db_index=True)),
                ('label', models.CharField(max_length=200, null=True, verbose_name='Label', blank=True)),
                ('score', models.IntegerField(help_text=b'This is the value saved in the DB')),
                ('mapped_score', models.IntegerField(help_text=b'The value to be used when computing scoresheets. Does not affect what is stored or exported.', null=True, blank=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChoiceSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(unique=True, max_length=64)),
                ('yaml', yamlfield.fields.YAMLField(default=b"\n1:\n  label: 'One'\n  score: 1\n2:\n  is_default_value: true\n  label: 'Two'\n  score: 2\n3:\n  label: 'More than two'\n  score: 2\n    ", blank=True, validators=[ask.validators.checkyamlchoiceset])),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(default=-1, help_text=b'The order in which items will apear in the page.', verbose_name=b'Page order')),
                ('allow_not_applicable', models.BooleanField(default=False)),
                ('required', models.BooleanField(default=False)),
                ('text', models.TextField(help_text='<p>The text displayed for this question.\n<a href="#" onClick="$(\'.questiontexthelp\').show();$(this).hide();return false;">\nSyntax help</a>\n<div class="questiontexthelp hide">\nAs part of instruction questions it\'s now possible to\ninclude variables representing summary scores (ScoreSheets) attached to\nthe Asker, or previous question responses.</p>\n<p>This is done by including Django template syntax in the <code>text</code> attribute\nof the question.</p>\n<p>Summary scores can be accessed as: <code>{{scores.&lt;scoresheetname&gt;.score}}</code>\nand computation messages as <code>{{scores.&lt;scoresheetname&gt;.message}}</code>.</p>\n<p>Previous answers can be displayed using <code>{{answers.&lt;variable_name&gt;}}</code>.</p>\n<p>Standard Django template logic can also be used with these variables,\nfor example <code>{% if scores.&lt;scoresheetname&gt;.score %}Show something else\n{% endif %}</code>.\n</div></p>', null=True, blank=True)),
                ('variable_name', models.SlugField(default=b'', max_length=32, validators=[ask.validators.first_char_is_alpha, ask.validators.illegal_characters, ask.validators.is_lower], help_text=b'Variable names can use characters a-Z,\n            0-9 and underscore (_), and must be unique within the system.', unique=True)),
                ('help_text', models.TextField(null=True, blank=True)),
                ('q_type', models.CharField(default=b'instruction', max_length=100, choices=[(b'instruction', b'instruction'), (b'likert', b'likert'), (b'likert-list', b'likert-list'), (b'pulldown', b'pulldown'), (b'required-checkbox', b'required-checkbox'), (b'checkboxes', b'checkboxes'), (b'long-text', b'long-text'), (b'open', b'open'), (b'short-text', b'short-text'), (b'integer', b'integer'), (b'decimal', b'decimal'), (b'slider', b'slider'), (b'range-slider', b'range-slider'), (b'date', b'date'), (b'date-time', b'date-time'), (b'time', b'time'), (b'hangup', b'hangup'), (b'upload', b'upload'), (b'webcam', b'webcam')])),
                ('extra_attrs', yamlfield.fields.YAMLField(help_text=b'A YAML representation of a python dictionary of\n        attributes which, when deserialised, is passed to the form widget when the questionnaire is\n        rendered. See django-floppyforms docs for options.', blank=True)),
                ('choiceset', models.ForeignKey(blank=True, to='ask.ChoiceSet', null=True)),
                ('page', models.ForeignKey(blank=True, to='ask.AskPage', null=True)),
                ('scoresheet', models.ForeignKey(blank=True, to='signalbox.ScoreSheet', null=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionAsset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text=b'A name to refer to this asset\n        with in the question_text field. To display an image or media\n        player within the question, include the text {{SLUG}} in the\n        question_text field of the question.')),
                ('asset', models.FileField(help_text=b'Can be an image (.jpg, .png, or .gif), audio file (.m4a, .mp4, or .mp3) or\n        movie (.mp4 only) for display as part of the question text.', null=True, upload_to=b'questionassets', blank=True)),
                ('template', models.CharField(max_length=255, choices=[(b'image.html', b'image'), (b'movie.html', b'movie'), (b'audio.html', b'audio')])),
                ('question', models.ForeignKey(to='ask.Question')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShowIf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('values', models.CharField(help_text=b'CASE INSENSITIVE values to match, comma separated. The question is shown if\n        any value matches', max_length=255, null=True, blank=True)),
                ('more_than', models.IntegerField(help_text=b'Previous question response\n        or summary score must be more than this value.', null=True, blank=True)),
                ('less_than', models.IntegerField(help_text=b'Previous question response\n        or summary score must be less than this value.', null=True, blank=True)),
                ('previous_question', models.ForeignKey(related_name=b'previous_question', blank=True, to='ask.Question', help_text=b'For previous values, enter the name of the question which\n        will already have been answered in this survey (technically, within this Reply)', null=True)),
                ('summary_score', models.ForeignKey(blank=True, to='signalbox.ScoreSheet', help_text=b'A summary score to be calculated based on answer already entered in the current\n        Reply.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='choice',
            name='choiceset',
            field=models.ForeignKey(blank=True, to='ask.ChoiceSet', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='choice',
            unique_together=set([('choiceset', 'score')]),
        ),
        migrations.AlterUniqueTogether(
            name='askpage',
            unique_together=set([('order', 'asker')]),
        ),
    ]
