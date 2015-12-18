# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings
import yamlfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('signalbox', '0002_studycondition_metadata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='replydata',
            options={'verbose_name': 'Reply meta data', 'verbose_name_plural': 'Reply meta data'},
        ),
        migrations.AlterField(
            model_name='alert',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='reminder',
            name='from_address',
            field=models.EmailField(help_text="<p>The email address you want the reminder to appear as if it\nhas come from. Think carefully before making this something other than\nyour own email, and be sure the smpt server you are using will accept\nthis  as a from address (if you're not sure, check). If blank this will be the\nstudy email. For SMS reminders the callerid will be the SMS return number\nspecified for the Study.</p>", max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='reply',
            name='entry_method',
            field=models.CharField(blank=True, max_length=100, null=True, choices=[(b'ad_hoc', b'Ad-hoc use of questionnaire'), (b'answerphone', b'Answerphone message'), (b'participant', b'Participant via the web interface'), (b'twilio', b'Twilio'), (b'double_entry', b'Double entry by an administrator'), (b'preview', b'Preview'), (b'anonymous', b'Anonymous survey response'), (b'ad_hoc_script', b'Data entered after ad-hoc script use')]),
        ),
        migrations.AlterField(
            model_name='study',
            name='ad_hoc_askers',
            field=models.ManyToManyField(help_text=b'Questionnaires which can be completed ad-hoc.', to='ask.Asker', verbose_name=b'Questionnaires available ad-hoc', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='ad_hoc_scripts',
            field=models.ManyToManyField(help_text=b"Scripts which can be initiated by users on an ad-hoc basis.\n        IMPORTANT. Scripts selected here will appear on the 'add extra data' tab\n        of participants' profile pages, and will display the name of the study,\n        and the name of the script along with the username of any related\n        membership. BE SURE THESE DO NOT LEAK INFORMATION you would not which\n        participants to see.", to='signalbox.Script', verbose_name=b'scripts allowed on an ad-hoc basis', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='createifs',
            field=models.ManyToManyField(help_text=b'Rules by which new observations might be made in response\n        to participant answers.', to='signalbox.ObservationCreator', verbose_name=b'Rules to create new\n        observations based on user responses', blank=True),
        ),
        migrations.AlterField(
            model_name='study',
            name='study_email',
            field=models.EmailField(help_text=b'The return email address for all mailings/alerts.', max_length=254),
        ),
        migrations.AlterField(
            model_name='studycondition',
            name='metadata',
            field=yamlfield.fields.YAMLField(help_text=b'YAML meta data available describing this condition. Can be used on Questionnaires, \n        e.g. to conditionally display questions.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='studycondition',
            name='scripts',
            field=models.ManyToManyField(to='signalbox.Script', blank=True),
        ),
        migrations.AlterField(
            model_name='usermessage',
            name='message_from',
            field=models.ForeignKey(related_name='from+', to=settings.AUTH_USER_MODEL),
        ),
    ]
