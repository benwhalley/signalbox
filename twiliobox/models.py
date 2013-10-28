#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException


class TwilioNumber(models.Model):
    """Studies reference a single phone number; details are stored here."""

    is_default_account = models.BooleanField(default=False)
    twilio_id = models.CharField(max_length=100)
    twilio_token = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100, unique=True, blank=True, null=True,
        help_text="""This must be a real twilio-provisioned number. Leave
        blank to populate automatically from the account details""")
    answerphone_script = models.ForeignKey('ask.Asker', blank=True, null=True)

    def __unicode__(self):
        return self.phone_number

    def number(self):
        return self.phone_number

    def client(self):
        if self.twilio_id and self.twilio_token:
            return TwilioRestClient(self.twilio_id, self.twilio_token)
        else:
            return None

    def get_caller_id_from_twilio_account_details(self):
        """Take the first available number for the account."""
        if self.client:
            numbers = self.client().phone_numbers.list()
            return numbers and numbers[0].phone_number
        else:
            return None

    def clean(self, *args, **kwargs):
        try:
            self.client()
            if not self.phone_number:
                self.phone_number = self.get_caller_id_from_twilio_account_details()
                # could send admin user a message here if we wanted...
        except TwilioRestException as e:
            raise ValidationError("Twilio credentials incorrect: {}".format(e))


        super(TwilioNumber, self).clean(*args, **kwargs)


    def save(self, *args, **kwargs):
        if self.is_default_account:
            for i in TwilioNumber.objects.all().exclude(id=self.id):
                i.is_default_account = False
                i.save()

        if not TwilioNumber.objects.filter(is_default_account=True).count():
            self.is_default_account = True
        super(TwilioNumber, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.is_default_account:
            if not TwilioNumber.objects.all().count() > 1:
                raise ValidationError("Can't delete last account.")
            randomother = TwilioNumber.objects.all()[0]
            randomother.is_default_account = True
            randomother.save()

        super(TwilioNumber, self).delete(*args, **kwargs)
