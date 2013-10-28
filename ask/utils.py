from ask.models import Question
from django.template.defaultfilters import slugify
import re


def statify(name, prefix=""):
    """
    Returns a valid Stata variable name, unique within the current database.
    """

    # kill anything which isn't ascii

    name = ''.join([x for x in name if ord(x) < 128])
    killwords = "i for to I'm about what with do is your how of the at please".split()
    name = re.sub(r'^\d+?\.?:?', "", name)
    namewords = name.lower().split()
    name = " ".join([i for i in namewords if i not in killwords])
    name = slugify(prefix + name)
    name = name.replace("-", "_")
    name = name[:30]
    matches = Question.objects.filter(variable_name__startswith=name).count()
    if matches > 0:
        name = name + "_" + str(matches)

    return name
