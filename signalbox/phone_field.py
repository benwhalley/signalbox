#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
import phonenumbers
from django.db import models
from django import forms
from django.conf import settings
from south.modelsinspector import add_introspection_rules
from phonenumbers import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException

DEFAULT_TELEPHONE_COUNTRY_CODE = settings.DEFAULT_TELEPHONE_COUNTRY_CODE

international_tuple = lambda x: (x.country_code, x.national_number)


def international_string(phone_number_obj):
    try:
        return phonenumbers.format_number(phone_number_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        return ""


def as_phone_number(value):
    if not value or isinstance(value, PhoneNumber):
        return value
    try:
        return phonenumbers.parse(value, settings.DEFAULT_TELEPHONE_COUNTRY_CODE)
    except NumberParseException:
        return PhoneNumber()


class PhoneNumberMultiWidget(forms.MultiWidget):

    def __init__(self, attrs=None):
        _widgets = (
            forms.TextInput(attrs={'size': 3, 'class': 'countrycode'}),
            forms.TextInput(attrs={'size': 12})
        )
        super(PhoneNumberMultiWidget, self).__init__(_widgets, attrs)

    def format_output(self, rendered_widgets):
        return """
        <table cellpadding=10>
            <tr>
                <td>+ {}<br/> Country code</td><td>{} <br/>Phone number (exclude leading zero)</td>
            </tr>
        </table>
        """.format(*rendered_widgets)

    def decompress(self, value):
        if value:
            return international_tuple(as_phone_number(value))
        else:
            return ["", ""]


class PhoneNumberMultiHiddenWidget(forms.MultipleHiddenInput):
    pass


class PhoneNumberFormField(forms.fields.MultiValueField):
    def __init__(self, *args, **kwargs):
        self.widget = PhoneNumberMultiWidget
        self.hidden_widget = PhoneNumberMultiHiddenWidget

        fields = (
            forms.fields.CharField(),
            forms.fields.CharField()
        )
        defaults = {
            "help_text": "Enter a phone number (country code / number)",
        }
        defaults.update(kwargs)
        super(PhoneNumberFormField, self).__init__(fields, *args, **defaults)

    def compress(self, value):
        if value and isinstance(value, list):
            value[0] = "+" + value[0]
        return "".join(value)


class PhoneNumberField(models.Field):

    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {
            "form_class": PhoneNumberFormField
        }
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)

    def to_python(self, value):
        if value:
            return as_phone_number(value)

    def get_prep_value(self, value):
        if value:
            return self.value_to_string(value)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 16
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def value_to_string(self, obj):
        if obj is not None:
            return international_string(obj)
        else:
            return self.get_default()


add_introspection_rules([], ["^signalbox\.phone_field\.PhoneNumberField"])
