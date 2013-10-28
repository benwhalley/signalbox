import os

HERE = os.path.realpath(os.path.dirname(__file__))
PROJECT_PATH, _ = os.path.split(HERE)


# Allows us to log users in from an email token
# See `start_data_entry()`
LOGIN_FROM_OBSERVATION_TOKEN = True

# django_registration
DEFAULT_FROM_EMAIL = "ben.whalley@plymouth.ac.uk"

# Standard django settings from here on...
SERVER_EMAIL = 'ben.whalley@plymouth.ac.uk'

ADMINS = (
    ('Ben Whalley', 'benwhalley@gmail.com'),
)
MANAGERS = (
    ('Ben Whalley', 'benwhalley@gmail.com'),
)

# Allows the user to see a list of their current studies.
SHOW_USER_CURRENT_STUDIES = True

DEFAULT_USER_PROFILE_FIELDS = [
    # list fields required for all studies
    # 'postcode',
]

