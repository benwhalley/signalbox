#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from ask.models import Asker, Question, AskPage

from django.contrib.auth import get_user_model
User = get_user_model()

from signalbox.models import Reply
from ask.forms import PageForm
from signalbox.utilities.djangobits import supergetattr


def start_anonymous_survey(request, asker_id, collector=None):
    # todo - could add a study id here to attach this all to? Or perhaps use different usernames
    # as collectors, like surveymonkey?

    asker = get_object_or_404(Asker, pk=asker_id)
    anonymous_user, created = User.objects.get_or_create(username="AnonymousUser")
    reply = Reply(asker=asker,
        user=anonymous_user,
        redirect_to=request.GET.get('next', "/"),
        entry_method="anonymous",
        collector=collector)
    reply.save()
    return HttpResponseRedirect(reverse('show_page', args=(reply.token,)))


def mock_page(questions):
    """Creates a temporary AskPage to use when previewing questions. -> AskPage"""
    page = AskPage(asker=Asker(id=99999999))
    page.save()
    [setattr(i, 'page', page) for i in questions]
    [setattr(i, 'order', j) for i, j in zip(questions, range(len(questions)))]
    return page  # remember to delete it, along with questions later


def page_preview(askpage, request):
    """Return a form which can be used to preview questions -> PageForm"""
    form = PageForm(request.POST or None, request.FILES or None,
                    page=askpage, reply=None, request=request)
    askpage.question_set.all().delete()
    askpage.delete()
    return form


@login_required
def preview_questions(request, ids):
    """Preview arbitrary questions, determined by CSV `ids' parameter -> HttpResponse"""

    idlist = [i for i in ids.split(",") if i]
    questions = Question.objects.filter(pk__in=idlist)
    page = mock_page(questions)
    form = page_preview(page, request)
    form.is_valid()

    return render_to_response(
        'admin/ask/question_preview.html', {'form': form, },
        context_instance=RequestContext(request))


def show_page(request, reply_token, preview=False):
    """Handles displaying and saving each page as a form -> HttpResponse or HttpResponseRedirect

    Note, there is a separate view for Twilio usage of questionnaires.
    """

    reply = get_object_or_404(Reply, token=reply_token)

    if not reply.open():
        messages.add_message(request, messages.ERROR, "Reply expired for new data entry.")
        return HttpResponseRedirect(reply.redirect_url())

    # todo replace this with Reply.objects.authorised()
    can_see_clinical = bool(request.user.groups.filter(
        name__in=['Researchers', 'Clinicians']).count())

    finishnow = bool(request.GET.get('finish', False))

    if request.POST:
        page = reply[int(request.POST.get('page_id'))]
        nextpage = request.GET.get('page', None)
    else:
        pagenum = request.GET.get('page', None)
        page = pagenum and reply[int(pagenum)] or reply.get_next_step(reply)

    if not page:
        page = reply[-1]  # get the last page

    form = PageForm(request.POST or None, request.FILES or None, page=page,
                    reply=reply, request=request)

    if page.is_last() and not page.questions_which_require_answers() and page.asker.finish_on_last_page:
        # if we want to leave participant on the last page we just capture
        # and ignore the return value of finish()
        _ = reply.finish(request)

    if form.is_valid():
        form.save(reply=reply, page=page)

        if finishnow and reply.is_complete():
            return reply.finish(request)

        url = reverse('show_page', kwargs={'reply_token': reply.token})
        if nextpage:
            url = url + "?page={}".format(nextpage)
        return HttpResponseRedirect(url)
    else:
        requires_more_responses = bool(page.questions_which_require_answers())
        showbutton = bool(page.is_last() or reply.is_complete() or len(list(reply)) == 1)
        showbutton = showbutton and requires_more_responses

        return render_to_response('asker_page.html',
            {
                'form': form,
                'page': page,
                'redbutton': showbutton,
                'hidemenu': page.asker.hide_menu,
                'reply': reply
            }, context_instance=RequestContext(request))


def print_asker(request, asker_id):
    """Returns full list of PageForms for Asker for print-ready output."""

    asker = get_object_or_404(Asker, id=asker_id)
    listofforms = [PageForm(request.POST or None, request=request, page=p, reply=None)
                   for p in asker.askpage_set.all()]

    return render_to_response('asker_print.html',
                              {'forms': [(i, i.conditional_questions)
                                         for i in listofforms], 'asker': asker, },
                              context_instance=RequestContext(request))
