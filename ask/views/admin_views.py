import re
import json
from datetime import datetime
from django.utils import encoding as en
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django import forms

from ask.forms import BulkAddQuestionsForm
from ask.models import Asker, Question, Instrument, ChoiceSet
from ask.models import truncatelabel
import ask.validators as valid
from ask.utils import statify
from django.contrib.auth.decorators import login_required
from signalbox.decorators import group_required
from signalbox.models import Reply
from django.core import serializers


class ImportInstrumentForm(forms.Form):

    jsonfile = forms.FileField(required=True)

    def clean(self):
        bitstoload = self.cleaned_data['jsonfile'].read()
        self.instrument = json.loads(bitstoload)[0]
        try:
            for obj in serializers.deserialize("json", bitstoload):
                obj.save()
            return self.cleaned_data
        except Exception as e:
            raise ValidationError(e)


@group_required(['Researchers', 'Research Assistants', ])
def show_codebook(request, asker_id=None):
    '''Displays a Stata-style codebook for all of a survey's variables'''

    askers = [get_object_or_404(Asker, id=int(asker_id))]
    return render_to_response('admin/ask/codebook.html',
        {'askers': askers}, context_instance=RequestContext(request))


@login_required
def preview_asker(request, asker_id=None, page_num=None):
    page_num = int(page_num) or 0
    a = get_object_or_404(Asker, id=asker_id)
    entry_method = page_num and "page_preview" or "preview"
    reply = Reply(asker=a, entry_method=entry_method, user=request.user)
    reply.save()
    reply.redirect_to = reverse('preview_reply', args=(reply.id, ))
    reply.save()
    url = reverse('show_page', kwargs={'reply_token': reply.token}) + "?page={}".format(page_num)
    return HttpResponseRedirect(url)


@group_required(['Researchers', 'Research Assistants'])
def bulk_add_questions(request):
    form = BulkAddQuestionsForm(request.POST or None)

    if request.POST and form.is_valid():
        fdata = form.cleaned_data
        instrument = fdata['add_to_instrument'] or Instrument(name="New instrument {}".format(datetime.now()))
        instrument.save()
        questions = [
            Question(
                instrument=instrument,
                text=q,
                variable_name=n,
                choiceset=fdata['choiceset'],
                q_type=fdata['q_type']
            )
            for q, n in zip(fdata['questions'], fdata['variable_names'])]


        try:
            map(lambda x: x.save(), questions)
            instrument.save()
        except Exception as e:
            raise ValidationError(str(e))

        return HttpResponseRedirect(reverse('admin:ask_instrument_change', args=(instrument.id, )))

    return render_to_response('admin/ask/bulk_add_questions.html',
        {'form': form},
        context_instance=RequestContext(request))
