from django.template.defaultfilters import slugify


def statify_label(text):
    text = slugify(text)
    for i in ["\n", "-"]:
        text = text.replace(i, " ")
    return text[:80]


def label_variable(question):
    return """label variable %(var)s "%(lab)s" \nnote %(var)s: %(full)s""" % {
        'var': question.variable_name,
        'lab': statify_label(question.text),
        'full': " ".join(question.text.splitlines())
    }


def label_choices(question):
    choicestring = " ".join(["""%s `"%s"' """ % (s, l) for s, l in question.choices()])
    return """label define %s %s """ % (question.variable_name, choicestring)


def label_choices_checkboxes(question):

    choicestring = " ".join(["""%s `"%s"' """ % (s, l) for s, l in question.choices()])
    labelsstring = """label define %s %s """ % (question.variable_name, choicestring)
    optionsstring = """
    tostring %s, replace
    split %s, p(",") destring gen(%s__ticked_)
    foreach v of varlist `r(varlist)' {
        label variable `v' `"%s"'
    }
    """ % tuple([question.variable_name] * 4)

    return "\n".join([labelsstring, optionsstring])


def set_format_time(question):
    """Times are exported as a CSV string of h:m:s and seconds since 00:00.

    Here we output stata syntax to split that string, and save and label the
    resulting 2 variables. """

    synt = """
    tostring %(var)s, replace
    split %(var)s, p(",") destring gen(%(var)s_split)
    label variable %(var)s_split1 "%(lab)s as a string"
    label variable %(var)s_split2 "%(lab)s as seconds since 00:00"
    destring %(var)s_split2, replace
    """ % {'var': question.variable_name, 'lab': statify_label(question.text)}

    return synt


def set_format_date(question):
    return """
tostring %s, replace
gen __tmpdate = date(%s,"YMD#")
drop %s
rename __tmpdate %s
format %s %%td
    """ % tuple([question.variable_name, ] * 5)


def set_format_datetime(question):
    return """
gen double __%s = clock(%s,"YMD#hms#")
drop %s
rename __%s %s
format %s %%tc
    """ % tuple([question.variable_name, ] * 6)
