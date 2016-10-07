# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shortuuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ask', '0004_auto_20161006_0809'),
    ]

    operations = [
        migrations.AddField(
            model_name='asker',
            name='allow_unauthenticated_download_of_anonymous_data',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='asker',
            name='anonymous_download_token',
            field=shortuuidfield.fields.ShortUUIDField(editable=False, blank=True, max_length=22),
        ),
    ]
