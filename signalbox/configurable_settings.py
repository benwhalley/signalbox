import sys
import string
from twilio.rest import TwilioRestClient
from signalbox.utilities.get_env_variable import get_env_variable


# determines numbers format on input for twilio
DEFAULT_TELEPHONE_COUNTRY_CODE = get_env_variable('DEFAULT_TELEPHONE_COUNTRY_CODE', default="GB")  
# this logs users in when they click a link in an email... see start_data-entry()
LOGIN_FROM_OBSERVATION_TOKEN = get_env_variable('LOGIN_FROM_OBSERVATION_TOKEN', default=False, int_to_bool=True)
SHOW_USER_CURRENT_STUDIES = get_env_variable('SHOW_USER_CURRENT_STUDIES', default=False, int_to_bool=True)


DEBUG = get_env_variable('DEBUG', int_to_bool=True, required=False, default=False)

# amazon files settings
AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME", default="thesignalbox")
COMPRESS_ENABLED = get_env_variable('COMPRESS_ENABLED', default=True, int_to_bool=True)
AWS_QUERYSTRING_AUTH = get_env_variable('AWS_QUERYSTRING_AUTH', default=False, int_to_bool=True)
# Set True for offline development with no access to S3 for static files
OFFLINE = get_env_variable('OFFLINE', default=False, int_to_bool=True)


# keep these secret
SECRET_KEY = get_env_variable('SECRET_KEY', default="1234")
AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID', default="")
AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY', default="")
TWILIO_ID = get_env_variable('TWILIO_ID', required=False)
TWILIO_TOKEN = get_env_variable('TWILIO_TOKEN', required=False)


# security-related settings
# see https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS', required=True).split(";")
SESSION_COOKIE_HTTPONLY = get_env_variable('SESSION_COOKIE_HTTPONLY', default=True, int_to_bool=True)
SECURE_BROWSER_XSS_FILTER = get_env_variable('SECURE_BROWSER_XSS_FILTER', default=True, int_to_bool=True)
SECURE_CONTENT_TYPE_NOSNIFF = get_env_variable('SECURE_CONTENT_TYPE_NOSNIFF', default=True, int_to_bool=True)
SECURE_SSL_REDIRECT = get_env_variable('SECURE_SSL_REDIRECT', required=False, default=False, int_to_bool=True)
SESSION_COOKIE_AGE = get_env_variable('SESSION_COOKIE_AGE', default=1.5 * 60 * 60)  # 1.5 hours in seconds
SESSION_SAVE_EVERY_REQUEST = get_env_variable('SESSION_SAVE_EVERY_REQUEST', default=True, int_to_bool=True)
SESSION_EXPIRE_AT_BROWSER_CLOSE = get_env_variable('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=True)


# see the impersonation middleware for details of what this allow
ALLOW_IMPERSONATION = get_env_variable('ALLOW_IMPERSONATION', default=False, int_to_bool=True)

# Turn on and off versioning
# This setting determines whether the Reversion machinery is employed to keep logs
# of changes to Answers, Observations etc. It's off by default, because it rapidly
# generates more data than is allowed by the free heroku plan, but is useful for
# funded studies.
USE_VERSIONING = get_env_variable('USE_VERSIONING', default=False, int_to_bool=True)








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

