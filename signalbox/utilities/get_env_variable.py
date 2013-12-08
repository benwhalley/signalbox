import os
import sys
from django.core.exceptions import ImproperlyConfigured
import yaml
from contracts import contract


@contract
def get_env_variable(var_name, required=True, default=None, as_yaml=True, warning=None):
    """Get the environment variable, process and return, or raise exception.

    :type var_name: string
    :type required: bool
    :type default: string|bool|None|int
    :type as_yaml: bool
    :type warning: string|None

    :rtype: string|bool|seq|int|None

    """

    if default is not None:
        required = False

    try:
        answer = os.environ[var_name]
        if as_yaml:
            answer = yaml.safe_load(answer)
        return answer

    except KeyError:
        if warning:
            sys.stdout.write("WARNING: {} not present in the environment\n".format(var_name))
            sys.stdout.write(warning + "\n")

        if required:
            raise ImproperlyConfigured("{} is required".format(var_name))
        else:
            return default
