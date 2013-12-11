from contracts import contract
from pyparsing import *
from signalbox.utilities.djangobits import supergetattr, int_or_None

@contract
def parse_conditional(condition, mapping_of_answers):
    """
    :type condition: string|None
    :type mapping_of_answers: dict
    :rtype: bool
    """

    if not condition:
        return True

    map_tuples = [(i,int_or_None(j)) for i, j in mapping_of_answers.items()
        if i and isinstance(int_or_None(j), int)]

    if not map_tuples:
        # default to hiding the question - only hide if we are sure we should
        return False

    replaceme = lambda i, j: j
    prev_matchers = [Literal(i).setParseAction(replaceWith(j)) for i, j in map_tuples]
    prev_answer = Or(prev_matchers)
    comparator = Word(nums)

    operator = oneOf("< > == <= => in".split())
    subexpression = (prev_answer + operator + comparator)('subexp')
    subexpression.setParseAction(lambda x: eval(" ".join(map(str, x.subexp))))

    boolean_operator = oneOf("or and not".split())
    expression = OneOrMore((subexpression + boolean_operator) | subexpression)
    expression.setParseAction(lambda x: eval(" ".join(map(str, x))))

    try:
        return expression.parseString(condition)[0]
    except NameError as e:
        # if we are missing one of the variables shown we default to showing the question
        print e
        return True
    except ParseException as e:
        print e
        return True
