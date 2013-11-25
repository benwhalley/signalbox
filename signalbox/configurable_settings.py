import os
import string
import sys

import dj_database_url
import shortuuid
from signalbox.utilities.get_env_variable import get_env_variable
from twilio.rest import TwilioRestClient

# determines numbers format on input for twilio
DEFAULT_TELEPHONE_COUNTRY_CODE = get_env_variable('DEFAULT_TELEPHONE_COUNTRY_CODE', default="GB")

# this logs users in when they click a link in an email... see start_data-entry()
LOGIN_FROM_OBSERVATION_TOKEN = get_env_variable('LOGIN_FROM_OBSERVATION_TOKEN', default=False)
SHOW_USER_CURRENT_STUDIES = get_env_variable('SHOW_USER_CURRENT_STUDIES', default=False)


DEBUG = get_env_variable('DEBUG', required=False, default=False)


# database
os.environ["REUSE_DB"] = "1"
# a sensible default
DB_URL = get_env_variable('DATABASE_URL', required=False, default="postgres://localhost/sbox")
DATABASES = {'default': dj_database_url.config(default=DB_URL)}


# amazon files settings
AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME", default="thesignalbox")
COMPRESS_ENABLED = get_env_variable('COMPRESS_ENABLED', default=True)
AWS_QUERYSTRING_AUTH = get_env_variable('AWS_QUERYSTRING_AUTH', default=False)

# keep these secret
SECRET_KEY = get_env_variable('SECRET_KEY', default=shortuuid.uuid())
AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID', default="")
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY', default="")
TWILIO_ID = get_env_variable('TWILIO_ID', required=False)
TWILIO_TOKEN = get_env_variable('TWILIO_TOKEN', required=False)


# security-related settings
# see https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS', default="127.0.0.1;.herokuapp.com").split(";")
SESSION_COOKIE_HTTPONLY = get_env_variable('SESSION_COOKIE_HTTPONLY', default=True)
SECURE_BROWSER_XSS_FILTER = get_env_variable('SECURE_BROWSER_XSS_FILTER', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = get_env_variable('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_SSL_REDIRECT = get_env_variable('SECURE_SSL_REDIRECT', required=False, default=False)
SESSION_COOKIE_AGE = get_env_variable('SESSION_COOKIE_AGE', default=1.5 * 60 * 60)  # 1.5 hours in seconds
SESSION_SAVE_EVERY_REQUEST = get_env_variable('SESSION_SAVE_EVERY_REQUEST', default=True)
SESSION_EXPIRE_AT_BROWSER_CLOSE = get_env_variable('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=True)

# SECURITY BITS WHICH ARE NOT CUSTOMISABLE FROM ENV VARS AT PRESENT XXX
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# disable secure cookies for debugging
SESSION_COOKIE_SECURE = not get_env_variable('DEBUG', False)
# this must be off for django cms content editing to work
SECURE_FRAME_DENY = False


# Turn on and off versioning
# This setting determines whether the Reversion machinery is employed to keep logs
# of changes to Answers, Observations etc. It's off by default, because it rapidly
# generates more data than is allowed by the free heroku plan, but is useful for
# funded studies.
USE_VERSIONING = get_env_variable('USE_VERSIONING', default=False)

# TWILIO #
TTS_VOICE = get_env_variable('TTS_VOICE', default='female')
TTS_LANGUAGE = get_env_variable('TTS_LANGUAGE', default='en-gb')



##### EMAIL #####

EMAIL_HOST = get_env_variable('EMAIL_HOST', required=False, default='localhost')
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', default="465", required=False))
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', required=EMAIL_HOST != "localhost")
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', required=EMAIL_HOST != "localhost")

if EMAIL_HOST == "localhost" and EMAIL_PORT != 25 and get_env_variable('DEBUG', as_yaml=True, required=False, default=False):
    EMAIL_PORT = 25
    print >> sys.stderr, "Resetting EMAIL_PORT to 25 because EMAIL_HOST is localhost"





# DO SOME EXTRA SETUP BASED ON THESE VALUES

# setup twilio based on settings above
if TWILIO_ID and TWILIO_TOKEN:
    TWILIOCLIENT = TwilioRestClient(TWILIO_ID, TWILIO_TOKEN)
else:
    TWILIOCLIENT = None


# load a customised frontend for the site
fe = get_env_variable('FRONTEND', required=False, default="frontend")
FRONTEND = str(fe)[:10]
assert set(FRONTEND).issubset(set(string.ascii_letters + "_-"))


try:
    TESTING = 'test' == sys.argv[1]
except IndexError:
    TESTING = False

# override setting above in testing because some tests need it
if bool('test' in sys.argv):
    print "Turning on versioning because we are testing"
    USE_VERSIONING = True



ALLOWED_UPLOAD_MIME_TYPES = [
    'application/pdf',
    'image/png',
    'image/jpeg',
    'image/gif',
]
