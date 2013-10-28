import phonenumbers
from phonenumbers.phonenumberutil import number_type, is_possible_number
from django.contrib.humanize.templatetags.humanize import naturalday
from datetime import datetime
from django.core.exceptions import ValidationError
from django.conf import settings
from signalbox.phone_field import PhoneNumber
from django.utils.safestring import mark_safe
from naturaltimes import parse_natural_date


def valid_natural_datetime(value):
    output = "relative to now (%s) <pre>   "

    results, errors = zip(*[parse_natural_date(t) for t in value.splitlines()])

    if sum([bool(i) for i in errors if i]):
        raise ValidationError(", ".join([i for i in errors if i]))

    return value


def valid_hour(value):
    try:
        assert int(value) in range(0, 23)
        return value
    except AssertionError:
        raise ValidationError("Valid hours are between 0 and 23.")


def valid_hours_list(value):
    hours = value.split(",")
    try:
        _ = [valid_hour(i) for i in hours]
        return value
    except ValidationError as e:
        raise


def in_minute_range(value):
    if not 0 < value < 60:
        raise ValidationError("Enter a number from 0 to 59.")
    return value


def only_includes_allowed_fields(value):
    """Convert value to a list of possible userprofile field names
    and check they are in the list of possible fields which could
    be added for a study."""
    fields = value.split()
    for i in fields:
        if i not in settings.USER_PROFILE_FIELDS:
            raise ValidationError("{} not allowed".format(i))
    return value


def no_count_property_in_syntax(value):
    if "count=" in value:
        raise ValidationError(
            """`count' parameter found. Use `max_number_observations'.""")
    return value


def date_in_past(value):
    """Return true if the date is before the present"""

    if value > datetime.now():
        raise ValidationError("This date can't be in the future.")


def is_24_hour(value):
    if -1 < value < 24:
        return True
    raise ValidationError('''Number must be between 0 and 23''')


def could_be_number(value):
    if is_possible_number(value) is False:
        raise ValidationError("Not a phone number")


def is_mobile_number(value):
    """Note, using phonenumbers lib, we allow for ambiguous numbers which could be mobiles in countries like USA."""
    try:
        assert number_type(value) in [1, 2]
    except AssertionError:
        raise ValidationError('''Not a mobile number.''')


def is_landline(value):
    try:
        assert number_type(value) is 0
    except AssertionError:
        raise ValidationError('''Not a landline number.''')


def is_number_from_study_area(value):
    from signalbox.models import Study
    VALID_COUNTRY_CODES = set(map(lambda x: int(x.valid_telephone_country_codes), Study.objects.all()))

    if value.country_code not in VALID_COUNTRY_CODES:
        raise ValidationError("Country code not allowed.")
