"""
Module which handles importing questionnaires in special markdown dialect
using yaml and pyparsing to process the input. Also see to_markdown functions on Question,
Asker etc for the reverse of this process.

This is somewhat a work in progress, and is for expert users only just now.


### could use lxml instead of yaml...
from ask.views.asker_text_editing import *

doc = etree.parse(open('/Users/ben/Desktop/dose.html'))

pages = doc.xpath("/questionnaire/page")
choicesets = doc.xpath("/questionnaire/page/choiceset")
scoresheets = doc.xpath("/questionnaire/scoresheet")
questions = doc.xpath("/questionnaire/page/question")

# check there are no repeat questions
assert max(zip(*Counter([i.get('variable_name')
    for i in questions]).most_common())[1]) == 1, "Question names are repeated"


asker = Asker.objects.get(slug="dose")
asker.askpage_set.all().delete()
pages_o = [AskPage(asker=asker, name=i.get('name', None)) for i in pages]


# XXX add updating or creating of choicesets here


# add attributes to questions to flatten somewhat
[i.set('page_number', str(i.getparent().getparent().index(i.getparent()))) for i in questions]
[i.set('order', str(i.getparent().index(i))) for i in questions]
questions_d = [dict(i.items()) for i in questions]

[i.update({'page': pages_o[int(i['page_number']) - 1]}) for i in questions_d]
[i.update({'choiceset': ChoiceSet.objects.get(name=i.get('choiceset'))}) for i in questions_d
    if i.get('choiceset')]


questions_o, _ = zip(*[get_or_modify(Question, {'variable_name': i.get('variable_name')}, i)
    for i in questions_d])

asker.save()
# save choicesets here
[i.save() for i in pages_o]
[i.save() for i in questions_o]


"""


from lxml import etree
from collections import Counter
import itertools
from contracts import contract
from pyparsing import *
from signalbox.settings import SCORESHEET_FUNCTION_NAMES, SCORESHEET_FUNCTION_LOOKUP
from ask.models import Asker, ChoiceSet, Question, AskPage, Choice, ShowIf
from ask.models import question
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from hashlib import sha1
from itertools import groupby, chain
from signalbox.models import Reply, ScoreSheet
from signalbox.decorators import group_required
from signalbox.utilities.djangobits import dict_map
import ast
import floppyforms as forms
import os
import re
from asker_text_editing_utils import _find_choiceset, get_or_modify

# parsing functions for the showif commands
CL = CaselessLiteral
_getvars = lambda s, l, toks: itertools.chain(*[Question.objects.filter(variable_name__istartswith=i) for i in toks])
_fun = oneOf(" ".join(SCORESHEET_FUNCTION_NAMES))('fun')
showif_components = _fun + CL("(") + OneOrMore(Word(alphanums + "_-")).setParseAction(_getvars)('questions') + CL(")")

@contract
def process_scoresheet_string(name, s):
    """
    :param s: "functioname(list of variables)"
    :type s: string
    :returns: A saved ScoreSheet instance
    :rtype: a
    """

    components = showif_components.parseString(s) # use pyparsing to get bits
    ss =  ScoreSheet(name=name, function=components.fun)
    ss.save()
    [ss.variables.add(i) for i in components.questions]
    return ss


class TextEditForm(forms.Form):

    source = forms.CharField(required=True,
        widget=forms.widgets.Textarea(attrs={'rows': 15}))

    def __init__(self, *args, **kwargs):
        self.asker = kwargs.pop('asker')
        initial = kwargs.get('initial', {})
        if not initial.get('source'):
            initial['source'] = self.asker.as_editable_text()
        kwargs['initial'] = initial
        super(TextEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        doc = etree.fromstring(self.cleaned_data.get("source"))
        pages = doc.xpath("/questionnaire/page")
        choicesets = doc.xpath("/questionnaire/choiceset")
        scoresheets = doc.xpath("/questionnaire/scoresheet")
        questions = doc.xpath("/questionnaire/page/question")

        # check there are no repeat questions
        assert max(zip(*Counter([i.get('variable_name')
            for i in questions]).most_common())[1]) == 1, "Question names are repeated"

        questionnaire = dict(doc.xpath("/questionnaire")[0].items())
        asker, _ = get_or_modify(Asker, {"id": self.asker.id}, questionnaire)

        self.cleaned_data.update({
                'pages': pages,
                'choicesets': choicesets,
                'scoresheets': scoresheets,
                'questions': questions,
                'asker': asker
            })
        return self.cleaned_data




    def save(self):

        asker = self.cleaned_data['asker']
        scoresheets = self.cleaned_data['scoresheets']
        choicesets = self.cleaned_data['choicesets']

        choicesets_dlist = [dict(i.items()) for i in choicesets]
        [i.update({'yaml': j.text}) for i, j in zip(choicesets_dlist, choicesets)]
        choicesets_oblist, _ = zip(*[get_or_modify(ChoiceSet, {'name': i.get('name')}, i) for i in choicesets_dlist])
        [i.save() for i in choicesets_oblist]


        # raise Exception(choicesets_dlist)

        # if scoresheets:
        #     [i.delete() for i in asker.scoresheets.all()]
        #     sses = [process_scoresheet_string(k, v) for k, v in scoresheets.items()]
        #     [asker.scoresheets.add(i) for i in sses]
        #     asker.save()

        # delete preview replies to allow editing if we've been testing
        # otherwise db integrity errors occur
        Reply.objects.filter(asker=asker, entry_method="preview").delete()

        choicesets = self.cleaned_data['choicesets']
        pages = self.cleaned_data['pages']
        questions = self.cleaned_data['questions']

        # start afresh to make the right number of pages
        [i.delete() for i in asker.askpage_set.all()]

        pages_o = [AskPage(asker=asker, name=j.get('name', None), order=i) for i, j in enumerate(pages)]
        [i.save() for i in pages_o]

        # add page numbers and ordering to questions
        [i.set('page_number', str(i.getparent().getparent().index(i.getparent()))) for i in questions]
        [i.set('order', str(i.getparent().index(i))) for i in questions]

        # make questions into dictionaries and update adding the qustion text and askpage objects
        questions_d = [dict(i.items()) for i in questions]
        [i.update({'text': j.text}) for i, j in zip(questions_d, questions)]
        [i.update({'page': pages_o[int(i['page_number'])]}) for i in questions_d]
        [i.update({'choiceset': ChoiceSet.objects.get(name=i.get('choiceset'))}) for i in questions_d
            if i.get('choiceset')]

        #update with choiceset objects
        [_find_choiceset(d) for d in questions_d]

        # get and modify the question objects with the new data.
        questions_o, _ = zip(*[get_or_modify(Question, {'variable_name': i.get('variable_name')}, i)
            for i in questions_d])

        [i.save() for i in questions_o]


        asker.save()

        return asker





@group_required(['Researchers', 'Research Assistants'])
def edit_yaml_asker(request, asker_id):
    asker = Asker.objects.get(id=asker_id)
    form = TextEditForm(request.POST or None, asker=asker)

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('edit_yaml_asker', args=(asker.id,)))

    return render_to_response(
        'admin/ask/text_asker_edit.html', {'form': form, 'asker': asker},
        context_instance=RequestContext(request))

