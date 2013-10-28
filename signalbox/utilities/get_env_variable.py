import os
import sys
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name, required=True, default=None, int_to_bool=False):
    """ Get the environment variable, process and return, or raise exception."""
    if default != None:
        required = False

    try:
        answer = os.environ[var_name]
        if int_to_bool:
            answer = bool(int(answer))
        return answer

    except KeyError:
        error_msg = "Set the %s env variable" % var_name

        if required:
            raise ImproperlyConfigured(error_msg)
        else:
            # print >> sys.stderr, 'Info: using default setting of {} for {}'.format(
                # default, var_name)
            return default
