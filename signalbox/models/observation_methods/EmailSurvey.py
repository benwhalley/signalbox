import json
from django.core.urlresolvers import reverse
from signalbox.models.observation_helpers import send_email, get_email_message_parts


def update(self, success):
    if success:
        self.touch()
        self.status = -2  # sent, response pending
        self.attempt_count += 1
        self.save()


def link(self):
    return reverse('start_data_entry', kwargs={'observation_token': self.token})


def do(self):
    """Send the email"""

    to_address, from_address, subject, message = get_email_message_parts(self)
    success, result = send_email(to_address, from_address, subject, message)

    self.add_data(key="attempt", value=json.dumps({'email': str(result),
        'message': message}))
    self.update(success)
    return (bool(success), result)
