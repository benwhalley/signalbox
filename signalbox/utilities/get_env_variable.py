import os
import sys
from django.core.exceptions import ImproperlyConfigured
import yaml

def get_env_variable(var_name, required=True, default=None, as_yaml=True):
    """ Get the environment variable, process and return, or raise exception."""
    if default != None:
        required = False

    try:
        answer = os.environ[var_name]
        if as_yaml:
            answer = yaml.safe_load(answer)
        return answer

    except KeyError:
        error_msg = "Set the %s env variable" % var_name

        if required:
            raise ImproperlyConfigured(error_msg)
        else:
            return default
