import sys
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from twiliobox.models import TwilioNumber
from signalbox.models import Observation
from django_extensions.db.models import TimeStampedModel
from validators import is_mobile_number
from phonenumber_field.modelfields import PhoneNumberField
from observation_helpers import send_email, send_sms


class Alert(models.Model):
    study = models.ForeignKey('signalbox.Study')
    email = models.EmailField(blank=True, null=True)
    mobile = PhoneNumberField(null=True, blank=True)
    condition = models.ForeignKey('ask.ShowIf')

    class Meta:
        app_label = 'signalbox'
        verbose_name = "Alerting rule"

    def alerted_who(self):
        """Return string of the person alerted (if there was one)."""
        return str(self.email or self.mobile or "nobody")

    def __unicode__(self):
        return "Alert {} if {}".format(self.alerted_who(), self.condition)


class AlertInstance(TimeStampedModel):
    reply = models.ForeignKey('signalbox.Reply')
    alert = models.ForeignKey('signalbox.Alert')
    viewed = models.BooleanField(default=False)

    class Meta:
        app_label = 'signalbox'
        verbose_name = "Alert"

    def do(self):
        subject, message = "Alert from SignalBox", self.__unicode__()

        if self.alert.email:
            _from = self.reply.observation.dyad.study.study_email
            send_email([self.alert.email], _from, subject, message)
            print >> sys.stderr, "sent alert email for reply {}".format(self.reply.id)

        if self.alert.mobile:
            _from = TwilioNumber.objects.get(is_default_account=True).phone_number
            send_sms(self.alert.mobile, _from, "{}\n{}".format(subject, message))
            print >> sys.stderr, "sent alert SMS for reply {}".format(self.reply.id)

    def __unicode__(self):
        return "Alert: {} {} ({})".format(self.alert.alerted_who(),
                                            self.alert.condition,
                                            self.created)
