import os
import sys
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import shortuuid
from django.contrib import messages
from signalbox.utilities.get_env_variable import get_env_variable
from twilio.exceptions import TwilioException
from twilio.rest import TwilioRestClient


#### VERSIONING ###

# Determines whether the Reversion machinery is employed to keep logs
# of changes to Answers, Observations etc. It's off by default, because it rapidly
# generates a lot of data, but is useful for complex studies.

USE_VERSIONING = get_env_variable('USE_VERSIONING', default=False)

# override setting above in testing because some tests need it
if bool('test' in sys.argv):
    print "Turning on versioning because we are testing"
    USE_VERSIONING = True


#### SIGNALBOX BEHAVIOURS ####

# allows user to see the studies they are currently a member of (can be confusing for large trials)
SHOW_USER_CURRENT_STUDIES = get_env_variable('SHOW_USER_CURRENT_STUDIES', default=False)

# this logs users in when they click a link in an email... see start_data-entry()
LOGIN_FROM_OBSERVATION_TOKEN = get_env_variable('LOGIN_FROM_OBSERVATION_TOKEN', default=False)

# comma separated list of fields to be required for all user signups
# see signalbox.setting for possible values.
DEFAULT_USER_PROFILE_FIELDS = get_env_variable('DEFAULT_USER_PROFILE_FIELDS', default="").split(",")

# File uploads #
ALLOWED_UPLOAD_MIME_TYPES = [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/gif',
]


#### EMAIL ####
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = get_env_variable('EMAIL_HOST', required=False)
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', required=False, default="587"))
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', required=False, )
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', required=False, )


#### FILES ####

# Amazon file storage #
AWS_STORAGE_BUCKET_NAME = get_env_variable('AWS_STORAGE_BUCKET_NAME', default="signalbox")
AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID', required=False,)
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY', required=False)



#### AUTOMATED TELEPHONY ####

TWILIO_ID = get_env_variable('TWILIO_ID', required=False)
TWILIO_TOKEN = get_env_variable('TWILIO_TOKEN', required=False)


# setup twilio based on settings above
try:
    TWILIOCLIENT = TwilioRestClient(TWILIO_ID, TWILIO_TOKEN)
except TwilioException:
    TWILIOCLIENT = None

# determines numbers format on input for twilio
DEFAULT_TELEPHONE_COUNTRY_CODE = get_env_variable('DEFAULT_TELEPHONE_COUNTRY_CODE', default="GB")
TTS_VOICE = get_env_variable('TTS_VOICE', default='female')
TTS_LANGUAGE = get_env_variable('TTS_LANGUAGE', default='en-gb')



# GOOGLE #
GOOGLE_TRACKING_ID = get_env_variable('GOOGLE_TRACKING_ID', default="")



# Message tags for django admin bootstrapped
MESSAGE_TAGS = {
            messages.SUCCESS: 'alert-success success',
            messages.WARNING: 'alert-warning warning',
            messages.ERROR: 'alert-danger error'
}
