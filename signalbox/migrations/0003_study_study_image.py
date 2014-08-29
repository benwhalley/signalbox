# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signalbox', '0002_remove_study_study_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='study_image',
            field=models.ImageField(storage=b'signalbox.s3.PrivateRootS3BotoStorage', null=True, upload_to=b'not required', blank=True),
            preserve_default=True,
        ),
    ]
