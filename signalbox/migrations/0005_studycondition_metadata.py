# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import yamlfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('signalbox', '0004_auto_20151026_1641'),
    ]

    operations = [
        migrations.AddField(
            model_name='studycondition',
            name='metadata',
            field=yamlfield.fields.YAMLField(help_text=b'YAML meta data available describing this condition. Can be used on Questionnaires, e.g. to conditionally display questions.', null=True, blank=True),
            preserve_default=True,
        ),
    ]
