"""Custom Signals for the Signalbox and Ask apps"""

import django.dispatch

sbox_anonymous_reply_complete = django.dispatch.Signal(providing_args=["reply", "request"])