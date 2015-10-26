# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ask', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='javascript',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
