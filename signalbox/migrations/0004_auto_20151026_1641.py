# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import signalbox.s3
import signalbox.models.answer


class Migration(migrations.Migration):

    dependencies = [
        ('signalbox', '0003_study_study_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='replydata',
            options={'get_latest_by': 'modified', 'verbose_name': 'Reply meta data', 'verbose_name_plural': 'Reply meta data'},
        ),
        migrations.AlterField(
            model_name='answer',
            name='upload',
            field=models.FileField(storage=signalbox.s3.CustomS3BotoStorage(querystring_expire=300, querystring_auth=True, acl='private'), null=True, upload_to=signalbox.models.answer.upload_file_name, blank=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='entry_method',
            field=models.CharField(blank=True, max_length=100, null=True, choices=[(b'participant_ad_hoc', b'Data entered after ad-hoc script use'), (b'ad_hoc', b'DEPRECATED NAME (Ad-hoc use of questionnaire)'), (b'double_entry', b'Double entry by an administrator'), (b'twiliocall', b'Twilio telephone call'), (b'twiliosms', b'Twilio SMS conversation'), (b'anonymous', b'Anonymous survey response'), (b'participant', b'Participant via the web interface'), (b'answerphone', b'Answerphone message'), (b'preview', b'Preview'), (b'twilio', b'DEPRECATED NAME (Twilio telephone call)'), (b'ad_hoc_script', b'DEPRECATED NAME (Data entered after ad-hoc script use)')]),
        ),
        migrations.AlterField(
            model_name='study',
            name='study_image',
            field=models.ImageField(storage=signalbox.s3.CustomS3BotoStorage(), null=True, upload_to=b'study/images/', blank=True),
        ),
    ]
