# -*- coding: utf-8 -*-

from itertools import groupby

from ask.models import ChoiceSet
from ask.models import Question
from ask.models.fields import FIELD_NAMES
from django.core.exceptions import ValidationError
from signalbox.models import ScoreSheet
from signalbox.utilities.djangobits import get_or_modify, flatten
import yaml
from signalbox.utilities.gibberish import random_stata_varname
from pyparsing import *

########## pyparsing definitions #############

# any number of ~ tildes to start
blockstart = Suppress(Literal("~") * 3 + ZeroOrMore(Literal("~")))

# names of things in header, e.g. class names, can't have and of {}~= in them
attrword = Word("".join([i for i in set(printables) - set("<>{}~=()")]))
classword = Literal(".").suppress() + attrword

# an identifier for the block
DEFIDSTRING = "__ID__REPLACE__ME__"
iden = Optional(Literal("#").suppress() + attrword, default=DEFIDSTRING)('iden')
iden.setParseAction(lambda s, loc, toks: toks[0] != DEFIDSTRING and toks[0] or random_stata_varname())

# parse the keyvals
_keyval = Group(attrword('key') + Literal("=").suppress() +
    (dblQuotedString.setParseAction(removeQuotes) | attrword)('val'))

# the whole header, e.g. ~~~{#name .class stuff=here}
header = Literal("{").suppress() + \
    iden + \
    ZeroOrMore(classword)('classes') + \
    ZeroOrMore(_keyval)('keyvals').setParseAction(lambda t: {k: v for k, v in t}) + \
    Literal("}").suppress()

hiddenLiteral = lambda x: Literal(x).suppress()

# choices are defined within the question text block on a new line following >>>
_choice = Optional(Literal("*")('isdefault'), default="") \
    + Word(nums)('score') \
    + Optional(hiddenLiteral("[") + Word(nums)('mapped_score') + hiddenLiteral("]")) \
    + Literal("=").suppress() + \
    SkipTo(LineEnd().suppress())('label').setParseAction(lambda t: t[0].strip())


# the text of the question
code = SkipTo(Literal(">>>").suppress() | Literal("~~~").suppress())

# choices are converted to yaml strings to save on the choiceset model.
# in future we might use json instead, but historical and simple for the moment
_choice.setParseAction(lambda t: {'score': t.score, 'label': t.label,
        'isdefault': bool(t.isdefault), 'mapped_score': t.mapped_score or t.score})
choices = Suppress(Literal(">>>")) + ZeroOrMore(_choice) + Literal("~~~").suppress()

# dose <- dose_smokes + dose_exacerbations
_functions = oneOf("min max mean sum")
variable = attrword('variable_name')
function = oneOf("sum min max")
expr = function('function') + Literal("(").suppress() + \
    Group(OneOrMore(variable))('variables') + Literal(")").suppress()
calculated_score = Suppress(Literal(">>>")) + attrword('name') + Literal("<-").suppress() + expr('expression')
page = LineStart() + Suppress(Literal("#")) + ZeroOrMore(Word(alphanums))('step_name') + LineEnd()


# the whole definition of a page or question block
block = (blockstart + header + code('code') + Optional(choices('choices') |
    calculated_score('calculated_score'))) | page

_yaml_header_start = Literal("-").suppress() * 3 + Optional(ZeroOrMore(Literal("-"))).suppress()
yaml_header = _yaml_header_start + SkipTo(Literal("---") | Literal("..."))('yaml')


ispage = lambda x: bool(x.step_name)
isnotpage = lambda x: not ispage(x)


############ END OF PYPARSING DEFINITIONS ############


def make_question_dict(blockParseResult):
    """Make a dictionary from a pyparsing parseResult question.

    :param blockParseResult: A parseResult
    :rtype: dict

    """

    qytypeclasslist = [i for i in blockParseResult.classes if i in FIELD_NAMES]

    d = {
        'variable_name': blockParseResult.iden.strip(),
        'text': blockParseResult.code.strip(),
        'q_type': qytypeclasslist and qytypeclasslist[0] or "instruction",
    }

    if blockParseResult.choices:
        numbereddict = {k: v for k, v in enumerate(blockParseResult.choices.asList())}
        yamlstring = yaml.safe_dump(numbereddict)
        d.update(
            {
                'choiceset':
                get_or_modify(
                    ChoiceSet,
                    {'name': d['variable_name']},
                    {'yaml': yamlstring}
                )[0],
            }
        )
    else:
        d.update({'choiceset': None})

    keyvals = blockParseResult.keyvals or {}
    classlist = blockParseResult.classes and blockParseResult.classes.asList()
    d.update({'extra_attrs': {k: v for k, v in list(keyvals.items())}})
    d.update({'extra_attrs': {k: v for k, v in list(keyvals.items())}})

    d['extra_attrs'].update({'classes': {k: True for k in classlist}})
    d.update({'required': 'required' in classlist})

    return d


def add_scoresheet_to_question(question, parseResult):
    cs = parseResult.calculated_score
    if cs:
        variables = Question.objects.filter(variable_name__in=cs.variables.asList())

        if len(variables) != len(cs.variables.asList()):
            raise ValidationError("Not all variables from scoresheet ({}) were matched.".format(cs.name))
        ss, _ = get_or_modify(ScoreSheet, {'name': cs.name},
            {'function': cs.function})
        ss.save()
        [ss.variables.add(i) for i in variables]
        ss.save()
        question.scoresheet = ss
        question.save()


def make_page_dict(blockParseResult):
    """Make a dictionary from a pyparsing parseResult question.

    :param blockParseResult: A parseResult
    :rtype: dict

    """
    d = {
        'step_name': " ".join(blockParseResult.step_name.asList()),
    }
    return d
