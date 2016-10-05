"""
Module which handles importing questionnaires in special markdown dialect
using pyparsing to process the input.
"""
from collections import defaultdict
from hashlib import sha1
from itertools import groupby, chain
import itertools
import json
import os
from pprint import pprint
import re

from ask import validators as vals
from ask.models import Asker, ChoiceSet, Question, AskPage, Choice, ShowIf
from ask.views.parse_definitions import (block, yaml_header, make_question_dict,
    make_page_dict, add_scoresheet_to_question, ispage, isnotpage)
from ask.yamlextras import yaml
import ast
from contracts import contract
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import never_cache
import floppyforms as forms
from signalbox.decorators import group_required
from signalbox.exceptions import DataProtectionException, SignalBoxMultipleErrorsException, SignalBoxException
from signalbox.models import Reply, ScoreSheet, Answer
from signalbox.settings import SCORESHEET_FUNCTION_NAMES, SCORESHEET_FUNCTION_LOOKUP
from signalbox.utilities.djangobits import dict_map, get_or_modify, flatten
from signalbox.utils import padleft


def append_error_to_form(form, field, error):
    d = form.errors.as_data()
    try:
        d[field] = d[field].append(error)
    except KeyError:
        d[field] = error
    return


class TextEditForm(forms.Form):

    text = forms.CharField(required=True,
        widget=forms.widgets.Textarea(attrs={'rows': 100, 'class': "mousetrap",}))


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
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

        try:
            asker, _, _ = get_or_modify(Asker, {"id": self.asker.id}, asker_yaml)
        except ValueError as e:
            raise forms.ValidationError("There was a problem with the form: {}".format(e))

        if not self.request.user.is_superuser and asker.reply_count():
            raise forms.ValidationError("This questionnaire has already been used, so you can't edit it.")

        # check variable names are valid and not used in other questionnaires
        variable_names = [i.iden for i in filter(isnotpage, blocks)]


        naughtyquestions = Question.objects.filter(variable_name__in=variable_names).exclude(page__asker=asker)
        if naughtyquestions.count():
            raise forms.ValidationError(
                "Some variable names are already in use by other questionnaires ({})".format(
                    ", ".join([i.variable_name for i in naughtyquestions])))


        # check all variables specified in scoresheets can be found
        scshts = [i for i in blocks if i.calculated_score]
        for i in scshts:
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

        # END OF CLEANING PART

        # START OF SAVING PART
        # This was part of the save method, but now do here wrapped in transaction
        # because we can't raise validation errors easily otherwise

        # group questions by page, using filter(bool) to get rid of empty pages
        questionsbypage = list(filter(bool,
                [list(filter(isnotpage, (i[1]))) for i in groupby(blocks, ispage)]))

        pages = list(filter(ispage, blocks))
        pages_d = [make_page_dict(i) for i in pages]

        # pad to make sure we have enough pages (e.g. if first questions are specified without a page)
        pages_d = padleft(pages_d, len(questionsbypage), {})

        [j.update({'asker': asker, 'order': i}) for i, j in enumerate(pages_d)]
        new_pages = [get_or_modify(AskPage, {'asker': asker, 'order': i['order']}, i)
            for i in pages_d]

        questionsbypage_dicts = [[make_question_dict(i) for i in j] for j in questionsbypage]

        # add askpages and ordering to questions
        [[q.update({'page': p, 'order': i}) for i, q in enumerate(plist)]
            for plist, p in zip(questionsbypage_dicts, list(zip(*new_pages))[0])]

        # make question objects in format [(question, created, modified), ...]
        questionsbypage_obs = [[get_or_modify(Question, {'variable_name': q['variable_name']}, q)
            for q in page] for page in questionsbypage_dicts]

        # save everything
        def trytosavequestion(q):
            errors = []
            try:
                q.full_clean()
            except Exception as e:
                errors.append(e)

            try:
                q.save()
            except Exception as e:
                errors.append(e)

            try:
                q.choiceset and q.choiceset.save()
            except Exception as e:
                errors.append(e)

            if any(errors):
                return [{'q': q, 'e': i} for i in errors]

        try:
            # wrap in transaction because is-valid shouldn't have has side effects in the DB
            with transaction.atomic():
                errors = list(itertools.chain(*list(filter(bool, list(itertools.chain(*[[trytosavequestion(i) for i in list(zip(*p))[0]] for p in questionsbypage_obs]))))))
                if any(errors):
                    raise SignalBoxMultipleErrorsException(errors)

        except SignalBoxMultipleErrorsException as e:
            [self.add_error(None,
                forms.ValidationError("Problem with: {}".format(i.get('q')), params=i)) for i in e.errors]

        # add scoresheets back in
        [[add_scoresheet_to_question(question, parseresult)
            for question, parseresult in zip(pageq, pagep)]
            for pageq, pagep in zip(list(zip(*questionsbypage_obs))[0], questionsbypage)]

        asker.save()

        # delete unused pages and questions which aren't in the created/updated sets
        def delete_question_if_unused(q, asker):
            try:
                q.delete()
            except DataProtectionException:
                # we don't delete question altogether, but do remove from pages
                [p.question_set.remove(q) for p in justpages if q in p.question_set.all()]
                pass

        justquestions = [i for i, c, m in itertools.chain(*questionsbypage_obs)]
        justpages = [i for i, c, m in new_pages]
        [p.delete() for p in set(asker.askpage_set.all()) - set(justpages)]
        [delete_question_if_unused(i, asker) for i in set(asker.questions()) - set(justquestions)]

        return asker

    def save(self):
        pass


@never_cache
@group_required(['Researchers', 'Research Assistants'])
def edit_asker_as_text(request, asker_id):
    asker = Asker.objects.get(id=asker_id)
    asker.reply_set.filter(entry_method="preview").delete()
    form = TextEditForm(request.POST or None, request=request, asker=asker, locked=False,
        initial={'text': asker.as_markdown()})

    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('edit_asker_as_text', args=(asker.id,)))

    return render_to_response(
        'admin/ask/text_asker_edit.html', {'form': form, 'asker': asker},
        context_instance=RequestContext(request))
