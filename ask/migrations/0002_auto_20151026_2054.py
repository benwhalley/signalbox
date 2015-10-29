# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signalbox', '0001_initial'),
        ('ask', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='showif',
            name='summary_score',
            field=models.ForeignKey(blank=True, to='signalbox.ScoreSheet', help_text=b'A summary score to be calculated based on answer already entered in the current\n        Reply.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionasset',
            name='question',
            field=models.ForeignKey(to='ask.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='choiceset',
            field=models.ForeignKey(blank=True, to='ask.ChoiceSet', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='page',
            field=models.ForeignKey(blank=True, to='ask.AskPage', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='question',
            name='scoresheet',
            field=models.ForeignKey(blank=True, to='signalbox.ScoreSheet', null=True),
            preserve_default=True,
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
        migrations.AddField(
            model_name='askpage',
            name='asker',
            field=models.ForeignKey(to='ask.Asker'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='askpage',
            unique_together=set([('order', 'asker')]),
        ),
    ]
