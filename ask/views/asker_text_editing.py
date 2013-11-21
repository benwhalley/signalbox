"""
Module which handles importing questionnaires in special markdown dialect
using pandoc to process the input. Also see to_markdown functions on Question,
Asker etc for the reverse of this process.

This is somewhat a work in progress, and is for expert users only just now.

"""

from hashlib import sha1
from itertools import groupby, chain
import itertools
import os
from pprint import pprint
import re
from collections import defaultdict

from ask.models import Asker, ChoiceSet, Question, AskPage, Choice, ShowIf
from ask.models import question
from ask.yamlextras import yaml
import ast
from contracts import contract
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import floppyforms as forms
from signalbox.decorators import group_required
from signalbox.models import Reply, ScoreSheet, Answer
from signalbox.settings import SCORESHEET_FUNCTION_NAMES, SCORESHEET_FUNCTION_LOOKUP
from signalbox.utilities.djangobits import dict_map, get_or_modify, flatten
from signalbox.utils import padleft
from ask.views.parse_definitions import block, yaml_header, make_question_dict, \
    make_page_dict, as_custom_markdown, add_scoresheet_to_question





class TextEditForm(forms.Form):

    text = forms.CharField(required=True,
        widget=forms.widgets.Textarea(attrs={'rows': 100}))

    def __init__(self, *args, **kwargs):
        self.asker = kwargs.pop('asker')
        initial = kwargs.get('initial', {})
        if not initial.get('text'):
            initial['text'] = as_custom_markdown(self.asker)
        kwargs['initial'] = initial
        self.base_fields['text'].widget.attrs['rows']=len(initial['text'].split("\n"))+10
        super(TextEditForm, self).__init__(*args, **kwargs)


    def clean(self):
        try:
            text = self.cleaned_data.get("text")
            asker_yaml = yaml.safe_load(yaml_header.searchString(text)[0][0])
            blocks = block.searchString(text)
        except Exception as e:
            raise forms.ValidationError(
                "There was a problem parsing the yaml:\n\n {}".format(e))

        asker, _ = get_or_modify(Asker, {"id":self.asker.id}, asker_yaml )

        # check all scoresheet variables match
        for i in blocks:
            if i.calculated_score:
                varlist = i.calculated_score.variables.asList()
                variables = Question.objects.filter(variable_name__in=varlist)
                if len(varlist) != variables.count():
                    raise forms.ValidationError(
                        "Not all scoresheet variables (for {}) were matched.".format(
                            i.calculated_score.name))


        self.cleaned_data.update({
                "asker": asker,
                "asker_yaml": asker_yaml,
                "blocks": blocks
            })

        return self.cleaned_data


    def save(self):

        asker = self.cleaned_data['asker']
        blocks = self.cleaned_data['blocks']

        ispage = lambda x: bool(x.step_name)
        isnotpage = lambda x: not ispage(x)

        # delete unused pages and questions
        [i.delete() for i in asker.askpage_set.all()]
        [i.delete() for i in asker.questions()]
        # if i.variable_name not in [i.variable_name for i in itertools.chain(*questionsbypage_obs)]]
        # raise Exception(blocks)

        # group by page, using filter(bool) to get rid of empty pages
        questionsbypage = filter(bool,
                [filter(isnotpage, (i[1])) for i in groupby(blocks, ispage)])

        pages = filter(ispage, blocks)
        pages_d = [make_page_dict(i) for i in pages]

        # pad to make sure we have enough pages (e.g. if first questions are specified without a page)
        pages_d = padleft(pages_d, len(questionsbypage), {})

        [j.update({'asker':asker, 'order': i}) for i, j in enumerate(pages_d)]
        pages_obs = [get_or_modify(AskPage, {'asker':asker, 'order':i['order']}, i)[0] for i in pages_d]

        questionsbypage_d = [[make_question_dict(i) for i in j]
            for j in questionsbypage]

        # add askpages and ordering to questions
        [[q.update({'page': p, 'order': i}) for i, q in enumerate(plist)]
            for plist, p in zip(questionsbypage_d, pages_obs)]

        # make question objects
        questionsbypage_obs = [[get_or_modify(Question, {'variable_name': q['variable_name']}, q)[0] for q in page] for page in questionsbypage_d]

        # save everything

        [[i.clean() for i in p] for p in questionsbypage_obs]
        [[i.save() for i in p] for p in questionsbypage_obs]
        [[i.choiceset.save() for i in p if i.choiceset] for p in questionsbypage_obs]

        # add scoresheets back in
        [[add_scoresheet_to_question(question, parseresult)
            for question, parseresult in zip(pageq, pagep)] for
                pageq, pagep in zip(questionsbypage_obs, questionsbypage)]

        asker.save()

        return asker


@group_required(['Researchers', 'Research Assistants'])
def edit_asker_as_text(request, asker_id):
    asker = Asker.objects.get(id=asker_id)

    asker.reply_set.filter(entry_method="preview").delete()
    nreplies = asker.reply_set.all().count()

    if nreplies:
        form = None
    else:

        form = TextEditForm(request.POST or None, asker=asker)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('edit_asker_as_text', args=(asker.id,)))

    return render_to_response(
        'admin/ask/text_asker_edit.html', {'form': form, 'asker': asker},
        context_instance=RequestContext(request))

