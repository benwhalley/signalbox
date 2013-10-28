import twilio
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template
from signalbox.utils import current_site_url
from signalbox.models.observation_helpers import *
from signalbox.phone_field import international_string



def update(self, success_status):
    if success_status > -1:
        self.increment_attempts()

    if success_status == 1:
        self.status = -1  # set to 'in progress'
        self.touch()

    self.save()


def do(self, test=False):
    """Send the SMS message."""

    client = self.dyad.study.twilio_number.client()

    success = -1
    tem = Template(self.created_by_script.script_body)
    con = Context(self.create_observation_context())
    message = tem.render(con)
    to_number = international_string(self.user.get_profile().mobile)
    from_number = self.dyad.study.twilio_number.number()

    try:
        success = 1
        result = client.sms.messages.create(to=to_number,
                        from_=from_number,
                        body=message,
                        status_callback=current_site_url() + reverse('sms_callback'),)

        self.add_data(key="external_id", value=result.sid)

    except twilio.TwilioException as e:
        success = -1
        result = str(e)
        self.add_data(key="failure", value=result)

    self.update(success)
    return (success, result)
