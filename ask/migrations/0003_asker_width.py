# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ask', '0002_auto_20151026_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='asker',
            name='width',
            field=models.PositiveIntegerField(default=12),
            preserve_default=True,
        ),
    ]
