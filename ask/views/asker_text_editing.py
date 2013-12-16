"""
Module which handles importing questionnaires in special markdown dialect
using pyparsing to process the input.
"""
from django.views.decorators.cache import never_cache
from hashlib import sha1
from itertools import groupby, chain
import itertools
import os
from pprint import pprint
import re
from collections import defaultdict

from ask import validators as vals
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
    make_page_dict, add_scoresheet_to_question, ispage, isnotpage


class TextEditForm(forms.Form):

    text = forms.CharField(required=True,
        widget=forms.widgets.Textarea(attrs={'rows': 100}))

    def __init__(self, *args, **kwargs):
        self.asker = kwargs.pop('asker')
        self.locked = kwargs.pop('locked')
        super(TextEditForm, self).__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super(TextEditForm, self).clean()
        try:
            text = self.cleaned_data.get("text")
            asker_yaml = yaml.safe_load(yaml_header.searchString(text)[0][0])
            blocks = block.searchString(text)
        except Exception as e:
            raise forms.ValidationError(
                "There was a problem parsing the text:\n\n {}".format(e))

        asker, _ = get_or_modify(Asker, {"id":self.asker.id}, asker_yaml )

        # check variable names are valid and not used in other questionnaires
        variable_names = [i.iden for i in filter(isnotpage, blocks)]

        invalid_names = [i for i in variable_names if any(
            (   (not vals.first_char_is_alpha(i)),
                vals._contains_illegal_chars(i),
            )
        )]
        if invalid_names:
            raise forms.ValidationError("Invalid variable names ({})".format(
                ", ".join(invalid_names)))

        naughtyquestions = Question.objects.filter(variable_name__in=variable_names).exclude(page__asker=asker)
        if naughtyquestions.count():
            raise forms.ValidationError(
                "Some variable names are already in use by other questionnaires ({})".format(
                    ", ".join([i.variable_name for i in naughtyquestions])))


        # check all variables specified in scoresheets can be found
        for i in blocks:
            if i.calculated_score:
                varset = set(i.calculated_score.variables.asList())
                questions_set = set(variable_names)
                if not varset.issubset(questions_set):
                    raise forms.ValidationError(
                        "Not all variables for scoresheet '{}' were matched: {}".format(
                            i.calculated_score.name,
                            ", ".join(varset.difference(questions_set))))

        # update the form with some parsed data
        self.cleaned_data.update({
                "asker": asker,
                "asker_yaml": asker_yaml,
                "blocks": blocks
            })

        return self.cleaned_data


    def save(self):

        asker = self.cleaned_data['asker']
        blocks = self.cleaned_data['blocks']

        # delete unused pages and questions
        [i.delete() for i in asker.askpage_set.all()]
        [i.delete() for i in asker.questions()]

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



@never_cache
@group_required(['Researchers', 'Research Assistants'])
def edit_asker_as_text(request, asker_id):
    asker = Asker.objects.get(id=asker_id)
    asker.reply_set.filter(entry_method="preview").delete()
    nreplies = asker.reply_set.all().count()>0
    form = TextEditForm(request.POST or None, asker=asker, locked=nreplies,
        initial={'text':asker.as_markdown()})

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('edit_asker_as_text', args=(asker.id,)))

    return render_to_response(
        'admin/ask/text_asker_edit.html', {'form': form, 'asker': asker},
        context_instance=RequestContext(request))

