"""Models to handle making contact with a Participant"""
from django.conf import settings
from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

from django.core.mail import send_mail

from django_fsm.db.fields import FSMField, transition

from signalbox.phone_field import international_string
from twiliobox.models import TwilioNumber

MESSAGE_TYPES = [(i, i) for i in ["Email", "SMS"]]


class ContactReason(models.Model):
    name = models.CharField(blank=True, max_length=256)
    followup_expected = models.BooleanField(default=True)

    class Meta:
        app_label = 'signalbox'
        ordering = ['name']

    def __unicode__(self):
        return self.name


class ContactRecord(models.Model):
    participant = models.ForeignKey(settings.AUTH_USER_MODEL)
    reason = models.ForeignKey(ContactReason, blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, related_name="added_by")
    notes = models.TextField(blank=True)

    @property
    def reason_str(self):
        if self.reason:
            return self.reason
        return "Unspecified reason"

    class Meta:
        app_label = 'signalbox'
        ordering = ['-added']

    def __unicode__(self):
        return "ContactRecord: %s: %s" % (self.participant, self.added)


class UserMessage(models.Model):
    message_type = models.CharField(max_length=80, verbose_name="Send as",
        choices=MESSAGE_TYPES, default=MESSAGE_TYPES[0])
    message_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="to",
        verbose_name="To", blank=False)
    message_from = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False,
        null=False, related_name="from")
    subject = models.CharField(blank=True, null=True, max_length=200)
    message = models.TextField(blank=True)
    state = FSMField(default='pending')
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "signalbox"
        permissions = (
            ("can_send_message", "Can send email/SMS to participant."),)
        ordering = ['-last_modified']

    def __unicode__(self):
        return "%s from %s to %s" % (self.message_type, self.message_from, self.message_to)

    def _send_sms(self):

        number = TwilioNumber.objects.get(is_default_account=True)
        client = number.client()
        to_number = international_string(self.message_to.get_profile().mobile)
        from_number = number.phone_number
        sms = client.sms.messages.create(
            to=to_number, from_=from_number, body=self.message)

        return sms

    def _send_email(self):
        mess = send_mail(self.subject, self.message, self.message_from.email,
                         (self.message_to.email,), fail_silently=False)
        return mess

    @transition(field=state, source='pending', target='sent', save=True)
    def send(self):
        f = getattr(self, "_send_" + self.message_type.lower())  # e.g. gets _send_sms()
        return f()
