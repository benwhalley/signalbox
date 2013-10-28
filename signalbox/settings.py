from utilities.get_env_variable import get_env_variable


TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-uk'
USE_I18N = False
USE_L10N = False


DATE_INPUT_FORMATS = ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%b %d %Y',
                      '%b %d, %Y', '%d %b %Y', '%d %b, %Y', '%B %d %Y',
                      '%B %d, %Y', '%d %B %Y', '%d %B, %Y')

DATETIME_INPUT_FORMATS = ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d',
                          '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y',
                          '%d/%m/%y %H:%M:%S', '%d/%m/%y %H:%M', '%d/%m/%y')


# TWILIO #
# XXX todo move this to environment variable
TTS_VOICE = 'female'
TTS_LANGUAGE = 'en-gb'


# SIGNALBOX
USER_PROFILE_FIELDS = [
    # this is the list of possible fields in the user profile
    # list in the order in which they should appear in the form
    # note, you can't simply add fields here - they must also be
    # defined on the UserProfile model.
    'landline',
    'mobile',
    'site',
    'address_1',
    'address_2',
    'address_3',
    'county',
    'postcode',
]


# XXX todo move this to environment variable
DEFAULT_USER_PROFILE_FIELDS = [
    # list fields required for all studies
    # 'postcode',
]

OB_DATA_TYPES = [
    ('external_id', "External reference number, e.g. a Twilio SID"),
    ('attempt', "Attempt"),
    ('reminder', "Reminder"),
    ('success', "Success"),
    ('failure', "Failure"),
    ('created', "Created"),
    ('timeshift', "Timeshift"),
]

OB_DATA_TYPES_DICT = dict(OB_DATA_TYPES)

STATUS_CHOICES_DICT = {
    0: "pending",
    -2: "email sent, response pending",
    -3: "due, awaiting completion",
    -1: "in progress",
    -4: "redirected to external service",
    1: "complete",
    -99: "failed"
}

STATUS_CHOICES = sorted(zip(STATUS_CHOICES_DICT.keys(), STATUS_CHOICES_DICT.values()), reverse=True)

# Could be expanded in future for minimization, etc.
ALLOCATION_CHOICES = (
    ("random", "Weighted random"),
    ("balanced_groups_adaptive_randomisation", "Adaptive (weighted) randomisation to balance conditions")
)

SMS_STATUSCODES = {
    'd': ('delivered', True),
    'f': ('failed', False),
    'e': ('error', False),
    'j': ('', False),
    'u': ('', False)
}

TITLE_CHOICES = [(i, i) for i in ['', 'Mr', 'Mrs', 'Ms', 'Miss', 'Dr', 'Prof', 'Rev']]
