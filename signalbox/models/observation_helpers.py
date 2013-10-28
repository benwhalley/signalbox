import phonenumbers
import sys
from django.template import Context, Template
from django.core import mail
from django.conf import settings
import smtplib
import socket
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site


def send_sms(_to, _from, message, client, callback_url=None):
    return client.sms.messages.create(to=_to,
                                      from_=_from,
                                      body=message,
                                      status_callback=callback_url)


def get_email_address_details(observation):
    """Get the address detsils for an observation -> ((to_address, ), from_address)"""

    to_address = (observation.dyad.user.email, )
    from_address = observation.dyad.study.study_email
    return (to_address, from_address)


def format_message_content(header, body, observation):
    """Use templates to render message body and subject -> (subject, message)."""

    con = Context(observation.create_observation_context())
    message = Template(body).render(con)
    subject = Template(header).render(con)

    return (subject, message)


def get_email_message_parts(observation):
    """Collate components for email -> ((to_address, ), from_address, subject, message)"""

    to_address, from_address = get_email_address_details(observation)
    script = observation.created_by_script
    subject, message = format_message_content(script.script_subject,
                                              script.script_body, observation)

    return (to_address, from_address, subject, message)


def send_email(to_address, from_address, subject, message):
    """Try to send an email -> (bool_success, str_status_message)"""

    if False in [bool(i) for i in to_address]:
        return (False, "No 'to' address")

    return_message = ""
    success = False
    try:
        mess = mail.EmailMessage(subject, message, from_address, to_address)
        mess.send()
        return_message = mess
        success = True

    except smtplib.SMTPException as e:
        return_message = e

    except socket.error as e:
        # catch this everything because of http://bugs.python.org/issue2118
        return_message = e

    return (success, return_message)
