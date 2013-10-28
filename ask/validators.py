import string
from django.core.exceptions import ValidationError
import magic
from django.conf import settings


def is_allowed_upload_file_type(value):
    try:
        ftype = magic.from_buffer(
        value.read(1024 * 4), mime=True)
        if ftype not in settings.ALLOWED_UPLOAD_MIME_TYPES:
            raise ValidationError(
                "{0} files not allowed. Allowed types are: {1} and {2}.".format(
                    ftype,
                    ", ".join(settings.ALLOWED_UPLOAD_MIME_TYPES[:-1]),
                    settings.ALLOWED_UPLOAD_MIME_TYPES[-1]
                )
            )
        return value
    except Exception as e:
        raise ValidationError(e)


def is_int(value):
    try:
        return int(value)
    except:
        raise ValidationError("Please enter a whole number")


def is_lower(value):
    if not value == value.lower():
        raise ValidationError("Variable names must be lower case.")
    return value


def first_char_is_alpha(value):
    if not value[0].isalpha():
        raise ValidationError(
            """First character of the variable name must be a letter.""")
    return value


# From the stata manual: A name is a sequence of one to 32 letters (A-Z and
# a-z), digits (0-9), and underscores (_). The first character of a name
# must be a letter or an underscore.

LEGAL_STATA_VARIABLE_NAME_CHARACTERS = list(
    '_-' + string.lowercase + string.uppercase + string.digits)


def illegal_characters(value):
    illegals = [
        i for i in value if i not in LEGAL_STATA_VARIABLE_NAME_CHARACTERS]
    if illegals:
        raise ValidationError(
            "Illegal characters found: %s" % ("".join(illegals), ))
    return value


def less_than_n_chars(value, n=32):
    if len(value) > n:
        raise ValidationError(
            """Variable name (%s...) is too long.""" % value[:20], )
    return value
