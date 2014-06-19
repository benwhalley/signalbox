import os
from datetime import datetime
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
from django.core.exceptions import ValidationError
import pandas as pd
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context, Template
from signalbox.decorators import group_required
from signalbox.models import Answer, Study, Reply, Question, Membership
from django.shortcuts import render_to_response, get_object_or_404
from signalbox.forms import SelectExportDataForm, get_answers, DateShiftForm


ANSWER_FIELDS_MAP = dict([
    ('id', 'id'),
    ('reply__id', 'reply'),
    ('question__q_type', 'qtype'),
    ('answer', 'answer'),
    ('question__variable_name', 'variable_name'),
])

ROW_FIELDS_MAP = dict([
    ('reply__id', 'reply'),
    ('reply__collector', 'collector'),
    ('reply__observation__id', 'observation'),
    ('reply__entry_method', 'entry_method'),
    ('reply__observation__n_in_sequence', 'observation_index'),
    ('reply__observation__due', 'due'),

    ('reply__is_canonical_reply', 'canonical'),
    ('reply__started', 'started'),
    ('reply__last_submit', 'finished'),
    ('reply__id', 'reply'),

    ('reply__observation__dyad__user__username', 'participant'),
    ('reply__observation__dyad__relates_to__user__username', 'relates_to_participant'),

    ('reply__observation__dyad__study__slug', 'study'),
    ('reply__observation__dyad__condition__tag', 'condition'),
    ('reply__observation__dyad__date_randomised', 'randomised_on'),
])


@group_required(['Researchers', ])
def export_data(request):
    form = SelectExportDataForm(request.POST or None)
    if not form.is_valid():
        return render_to_response('manage/export_data.html', {'form': form},
                              context_instance=RequestContext(request))

    studies = form.cleaned_data['studies']
    questionnaires = form.cleaned_data['questionnaires']

    if studies:
        answers = get_answers(studies)

    if questionnaires:
        answers = Answer.objects.filter(reply__asker__in=questionnaires)

    if not answers.exists():
        raise ValidationError("No data matching filters.")

    answers = answers.filter(question__variable_name__isnull=False)
    return export_answers(request, answers)


def export_answers(request, answers):
    "Take a queryset of Answers and export to a zip file."

    # extract dicts
    ad = answers.values(*ANSWER_FIELDS_MAP.keys())
    rd = answers.values(*ROW_FIELDS_MAP.keys())

    # make dataframes
    answerdata = pd.DataFrame({i['id']: i for i in ad}).T
    rowmetadata = pd.DataFrame((i for i in rd))

    # rename columns
    answerdata.columns = [ANSWER_FIELDS_MAP[i] for i in answerdata.columns]
    rowmetadata.columns = [ROW_FIELDS_MAP[i] for i in rowmetadata.columns]

    # process
    answerdata = answerdata.set_index(['reply', 'variable_name']).unstack()['answer']
    rowmetadata = rowmetadata.drop_duplicates('reply').set_index('reply')

    # make excel files and others
    namesofthingstoexport = "answers meta".split()
    tmpfiles = [NamedTemporaryFile(suffix=".xlsx") for i in namesofthingstoexport]
    # write the data as xls not csv to preserve date formatting; requires xlwt
    [j.to_excel(i.name, merge_cells=False, encoding='utf-8') for i, j in zip(tmpfiles, [answerdata, rowmetadata])]

    makedotmp = get_template('signalbox/stata/make.dotemplate')
    makedostring = makedotmp.render(Context({'date': datetime.now(), 'request': request}))

    # make a syntax file to label everything
    questions = set((i.question for i in answers))
    choicesets = set(filter(lambda x: x.get_choices(), (i.choiceset for i in questions if i.choiceset)))
    syntaxtdotmp = get_template('signalbox/stata/process-variables.dotemplate')
    syntax_dostring = syntaxtdotmp.render(Context({'questions': questions, 'choicesets': choicesets, 'request':request}))

    # make zip and return bytes
    with ZipFile(NamedTemporaryFile(suffix=".zip").name, 'w') as zipper:
        [zipper.write(i.name, j + os.path.splitext(i.name)[1]) for i, j in zip(tmpfiles, namesofthingstoexport)]
        zipper.writestr('make.do', makedostring)
        zipper.writestr('make_labels.do', syntax_dostring)

        zipper.close()
        zipbytes = open(zipper.filename, 'rb').read()

        response = HttpResponse(zipbytes, content_type='application/x-zip-compressed')
        response['Content-disposition'] = "attachment; filename=exported_data.zip"

        return response


def generate_syntax(template, questions, reference_study=None):
    """Return a string of stata syntax to format exported datafile for a given set of questions."""

    t = get_template(template)
    syntax = t.render(
        Context({'questions': questions, 'reference_study': reference_study})
    )
    return syntax


def _shifted(obj, datetimefield, delta):
    setattr(obj, datetimefield, getattr(obj, datetimefield) + delta)
    return obj

from signalbox.utilities.djangobits import conditional_decorator
from django.conf import settings
import reversion

@group_required(['Researchers', ])
@conditional_decorator(reversion.create_revision, settings.USE_VERSIONING)
def dateshift_membership(request, pk=None):
    '''Allows Researchers to shift the time of all observations within a Membership.'''

    membership = get_object_or_404(Membership, id=pk)
    form = DateShiftForm(request.POST or None)
    if form.is_valid():

        # calclate difference from current randomisation date and shift randomisation date
        delta = form.delta(current=membership.date_randomised)
        membership.date_randomised = membership.date_randomised + delta
        membership.save()

        shiftable = [i for i in membership.observations(
        ) if i.timeshift_allowed()]
        shifted = [_shifted(i, 'due', delta) for i in shiftable]
        shifted = [_shifted(i, 'due_original', delta) for i in shiftable]

        _ = [i.add_data("timeshift", value=delta) for i in shifted]
        _ = [i.save() for i in shifted]

        if settings.USE_VERSIONING:
            revision.comment = "Timeshifted observations by %s days." % (delta.days,)

        form = DateShiftForm(
        )  # wipe the form to make it harder to double-submit by accident
        messages.add_message(request, messages.WARNING,
            """{} observations shifted by {} days.""".format(len(shifted), delta.days))

        return HttpResponseRedirect(reverse('admin:signalbox_membership_change', args=(membership.pk,)))

    return render_to_response('admin/signalbox/dateshift.html',
                              {'form': form, 'membership': membership}, context_instance=RequestContext(request))
