import json
from signalbox.models import observation_helpers as hlp


def update(self, success):
    if success:
        self.touch()
        self.status = 1
        self.save()


def do(self):
    """Send the email and save a record."""

    to, from_address, subject, message = hlp.get_email_message_parts(self)
    success, result = hlp.send_email(to, from_address, subject, message)

    self.add_data(key="attempt", value=json.dumps({'email': str(result),
        'message': message}))
    self.update(success)
    return (bool(success), result)
