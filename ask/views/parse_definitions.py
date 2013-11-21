from django.core.exceptions import ValidationError
from signalbox.utilities.djangobits import get_or_modify, flatten
from statlib import stats
from itertools import groupby
from ask.models import ChoiceSet
from pyparsing import *
import shortuuid
import yaml
from ask.models.fields import FIELD_NAMES
from ask.models import Question
from signalbox.models import ScoreSheet

########## pyparsing definitions #############

# any number of ~ tildes to start
blockstart = OneOrMore(Literal("~"))

# names of things in header, e.g. class names, can't have and of {}~= in them
attrword = Word("".join([i for i in set(printables)-set("<>{}~=()")]))
classword = Literal(".").suppress() + attrword

# an identifier for the block
DEFIDSTRING = "__ID__REPLACE__ME__"
iden = Optional( Literal("#").suppress() + attrword, default=DEFIDSTRING)('iden')
iden.setParseAction(lambda s, loc, toks: toks[0] != DEFIDSTRING and toks[0] or shortuuid.uuid().lower())

# parse the keyvals
_keyval = Group(attrword('key') + Literal("=").suppress() + \
    (dblQuotedString.setParseAction(removeQuotes)|attrword)('val'))

# the whole header, e.g. ~~~{#name .class stuff=here}
header = Literal("{").suppress() + \
    iden + \
    ZeroOrMore(classword)('classes') + \
    ZeroOrMore(_keyval)('keyvals').setParseAction(lambda t: {k:v for k, v in t}) + \
    Literal("}").suppress()

# choices are defined within the question text block on a new line following >>>
_choice = Word(nums)('score') \
    + Optional(Literal("*")('isdefault'), default="") \
    + Literal("=").suppress() + \
    SkipTo(LineEnd().suppress())('label').setParseAction(lambda t: t[0].strip())


# the text of the question
code = SkipTo(Literal(">>>").suppress()|Literal("~~~").suppress())

# choices are converted to yaml strings to save on the choiceset model.
# in future we might use json instead, but historical and simple for the moment
_choice.setParseAction(lambda t: {'score': t.score,  'label':t.label, 'isdefault': bool(t.isdefault)})
choices = Suppress(Literal(">>>")) + ZeroOrMore(_choice) + Literal("~~~").suppress()

# dose <- dose_smokes + dose_exacerbations
_functions = oneOf("min max mean sum")
# _functions_map = {'min': min, 'max': max, 'sum':sum, 'mean':stats.lmean}
variable = attrword('variable_name')
function = oneOf("sum min max")
expr = function('function') + Literal("(").suppress() + Group(OneOrMore(variable))('variables') + Literal(")").suppress()
calculated_score = Suppress(Literal(">>>")) + attrword('name') + Literal("<-").suppress() + expr('expression')
page = LineStart() + Suppress(Literal("#")) + ZeroOrMore(Word(alphanums))('step_name') + LineEnd()


# the whole definition of a page or question block
block = (header + code('code') + Optional(choices('choices')|calculated_score('calculated_score'))) | page

_yaml_header_start = Literal("-").suppress()*3 + Optional(ZeroOrMore(Literal("-"))).suppress()
yaml_header = _yaml_header_start + SkipTo(Literal("---")|Literal("..."))('yaml')


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
            {'choiceset':
                get_or_modify(ChoiceSet, {'name':d['variable_name']}, {'yaml':yamlstring})[0],
            }
        )
    keyvals = blockParseResult.keyvals or {}
    classlist = blockParseResult.classes and blockParseResult.classes.asList()
    d.update({'widget_kwargs': {k: v for k, v in keyvals.items()}})
    d.update({'required': 'required' in classlist})

    return d


def add_scoresheet_to_question(question, parseResult):
    cs = parseResult.calculated_score
    if cs:
        variables = Question.objects.filter(variable_name__in=cs.variables.asList())

        if len(variables) != len(cs.variables.asList()):
            raise ValidationError("Not all variables from scoresheet ({}) were matched.".format(cs.name))
        ss, _ = get_or_modify(ScoreSheet, {'name': cs.name},
            {'function':cs.function,})
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




def _find_choiceset(d):
    if d.get('choiceset'):
        cs, _ = ChoiceSet.objects.get_or_create(name=d.get('choiceset'))
    else:
        cs = None
    d.update({'choiceset': cs})
    return d



# xxx move these to be methods on the objects

def choiceset_as_markdown(choiceset):
    if not choiceset.yaml:
        choiceset.yaml = {i:d for i, d in enumerate([{'score':x.score, 'isdefault': x.is_default_value, 'label':x.label} for x in choiceset.get_choices()])}

    return "\n".join([
        u"""{}{}={} """.format(c['score'], c.get('isdefault', "") and "*" or "", c['label'])
            for i, c in choiceset.yaml.items()])

def page_as_markdown(page):
    return u"\n\n# {}\n".format(page.step_name or "")

from django.forms.models import model_to_dict

def scoresheet_as_markdown(scoresheet):
    d = model_to_dict(scoresheet)
    d.update({'variable_string': " ".join([i.variable_name for i in scoresheet.variables.all()])})
    return """\n{name} <- {function}({variable_string})""".format(**d)

def question_as_markdown(question):

    # iden = question.q_type != "instruction" and "#"+question.variable_name or ""
    iden = "#"+question.variable_name
    classesstring = " ".join(["."+i for i in [question.q_type]])
    classesstring += question.required and " .required" or ""
    keyvals = dict(question.widget_kwargs)
    keyvalsstring = " ".join(["""{}="{}" """.format(k, v) for k, v in keyvals.items()])
    detailsstring = ""
    if question.choiceset:
        detailsstring = u">>>\n" + choiceset_as_markdown(question.choiceset)
    elif question.scoresheet:
        detailsstring = u">>>\n"+scoresheet_as_markdown(question.scoresheet)

    return u"""~~~{{{} {} {} }}\n{}\n{}\n~~~""".format(iden, classesstring, keyvalsstring, question.text, detailsstring)


def as_custom_markdown(asker):
    """A helper to convert an asker and associated questions to our custom markdown
    format. In future this should migrate to the asker model."""


    askerasyaml = yaml.safe_dump({
            'slug':asker.slug,
            'name':asker.name,
            'steps_are_sequential': asker.steps_are_sequential,
            'redirect_url': asker.redirect_url,
            'finish_on_last_page': asker.finish_on_last_page,
            'show_progress': asker.show_progress,
            'success_message': asker.success_message,
        }, default_flow_style=False)

    allqs = [(i, i.get_questions()) for i in asker.askpage_set.all()]
    allqs = map(lambda x: (page_as_markdown(x[0]), x[1]), allqs)
    allqs = [(i[0], map(question_as_markdown, i[1])) for i in allqs]

    x = flatten(allqs)
    x = flatten(x)
    return "---\n" + askerasyaml + "---\n\n" + "\n\n".join(x)

