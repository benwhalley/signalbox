#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.contrib import messages
from django.db import models

from django.conf import settings
User = settings.AUTH_USER_MODEL


from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from shortuuidfield import ShortUUIDField
from signalbox.models.scoresheet import ScoreSheet
from signalbox.utilities.linkedinline import admin_edit_url
from answer import Answer
from signalbox.process import Step, ProcessManager
from signalbox.utilities.djangobits import supergetattr
from signalbox.utilities.mixins import TimeStampedModel


ENTRY_METHOD_LOOKUP = {
    'double_entry': "Double entry by an administrator",
    'preview': "Preview",
    'participant': "Participant via the web interface",
    'twilio': "Twilio",
    'ad_hoc': "Ad-hoc use of questionnaire",
    'ad_hoc_script': "Data entered after ad-hoc script use",
    'anonymous': "Anonymous survey response",
    'answerphone': "Answerphone message",
}


class ReplyManager(models.Manager):

    def authorised(self, user):
        """Provide per-user access for Replies."""

        qs = super(ReplyManager, self).select_related()

        if user.is_superuser:
            return qs

        qs = qs.exclude(
            observation__created_by_script__allow_display_of_results=False)

        if not user.groups.filter(name="Clinicians").count() > 0:
            qs = qs.exclude(
                observation__created_by_script__is_clinical_data=True)

        return qs


class ReplyData(TimeStampedModel):
    """Meta data related to a Reply, for example UUIDs from externally called services."""
    reply = models.ForeignKey('signalbox.Reply')
    key = key = models.CharField(max_length=255, choices=settings.REPLY_DATA_TYPES, db_index=True)
    value = models.TextField(blank=True, null=True)

    class Meta():
        app_label = 'signalbox'
        verbose_name = "Reply meta data"
        verbose_name_plural = "Reply meta data"


class Reply(models.Model, ProcessManager):

    '''Organises a set of Answers and tracks Asker completion.'''

    def answers_ordered_as_per_original_asker(self):
        """Used in place of self.answer_set, mimics ordering of Asker used."""
        if not self.asker:
            return self.answer_set.all()

        ordered_questions = list(self.asker.questions())
        unordered_anwers = self.answer_set.all()
        answers_dict = {i.variable_name(): i for i in unordered_anwers}

        # insert 'faked' answers to enable user to see questions which were
        # not attempted in this reply.
        # note, must enumerate them and add a pk because of this issue:
        # https://code.djangoproject.com/ticket/18864
        ordered_answers = [answers_dict.get(
            i.variable_name,
            Answer(question=i, pk=j)) for j, i in enumerate(ordered_questions)]

        # add any additional answers - should just be page_id really
        remaining_variables = set(unordered_anwers) - set(ordered_answers)
        map(
            lambda x: ordered_answers.append(
                answers_dict.get(x.variable_name(), x)),
            remaining_variables)

        return ordered_answers

    def mapping_of_answers_and_scores(self):
        """
        Create a mapping of all answers and summary scores in this Reply
        :rtype: dict
        """

        mapping = {
            supergetattr(i, 'question.variable_name', i.other_variable_name): i.answer
            for i in self.answer_set.all()
        }
        mapping.update({k: v.get('score', None) for k, v in self.asker.summary_scores(self).items()})
        return mapping

    def add_data(self, key, value):
        """Add a ReplyData object for this Reply, save it, and return it.
        :type key: string
        :type value: string
        """

        d = ReplyData(reply=self, key=key, value=value)
        d.save()
        return d

    def __iter__(self):
        """Returns a series of pages: steps to complete within the reply."""

        if self.entry_method == "twilio":
            # we split by question if this is a telephone call
            for i in self.asker.questions():
                yield i
        else:
            # otherwise split into pages
            for i in self.asker.askpage_set.all().iterator():
                yield i

    objects = ReplyManager()

    is_canonical_reply = models.BooleanField(default=False,)

    observation = models.ForeignKey(
        'signalbox.Observation', blank=True, null=True)

    # we have links to both Observations and Memberships because of
    # signalbox.views.replies.use_adhoc_asker
    membership = models.ForeignKey(
        'signalbox.Membership', blank=True, null=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name="reply_user",
        help_text="""IMPORTANT: this is not necessarily the user providing the data (i.e. a
        patient) but could be an assessor or admin person doing double entry from paper. It
        could also be null, where data is added by an AnonymousUser (e.g. Twilio or external
        API which doesn't authenticate.)""")

    asker = models.ForeignKey('ask.Asker', null=True, blank=True,)

    redirect_to = models.CharField(max_length=1000, null=True, blank=True,)

    last_submit = models.DateTimeField(null=True, blank=True, auto_now=True)

    started = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    originally_collected_on = models.DateField(null=True, blank=True,
       help_text="""Set this if the date that data were entered into the system is not the date
        that the participant originally provided the responses (e.g. when retyping paper data)""")

    complete = models.BooleanField(default=False, db_index=True)

    token = ShortUUIDField(auto=True)

    external_id = models.CharField(null=True, blank=True, max_length=100,
                        help_text="""Reference for external API, e.g. Twilio""")

    entry_method = models.CharField(
        choices=[(k, v) for k, v in ENTRY_METHOD_LOOKUP.items()],
        max_length=100, null=True, blank=True,)

    notes = models.TextField(null=True, blank=True,)

    collector = models.SlugField(null=True, blank=True)

    def open(self):
        """Can data be added for this reply? -> Bool"""

        if self.complete:
            return False

        if self.last_submit < datetime.now() - timedelta(days=1):
            # Replies time out after 1 day as a default.
            return False

        if self.observation and "double_entry" not in self.entry_method:
            # Observation windows also apply, unless we are doing double entry of data in the admin interface.
            obsisopen, _ = self.observation.open_for_data_entry()
            return bool(obsisopen)

        return True

    def relevant_scoresheets(self):
        return self.asker.scoresheets()

    def computed_scores(self):
        scoresheets = self.relevant_scoresheets()
        answers = self.answer_set.all()
        if self.observation:
            return [i.compute(answers) for i in scoresheets]

    def is_preview(self):
        if self.entry_method == "preview":
            return True
        return False

    def number_replies_made_for_observation(self):
        """Convenience method for use in the admin"""
        return self.observation.reply_set.all().count()

    def is_preferred_reply(self):
        """Returns whether this was the Reply to use for an Observation."""

        replies = self.observation.reply_set.all()
        if replies.count() == 1:
            return True
        else:
            canon = replies.filter(is_canonical_reply=True)
            return bool(self in canon)

    def redirect_url(self):
        return self.redirect_to or \
            supergetattr(self, "created_by_script.asker.redirect_url", None) or reverse('user_homepage')

    def number_non_empty_answers(self):
        return len([i for i in self.answer_set.all().exclude(
            other_variable_name="page_id").exclude(
                question__q_type="instruction") if i.answer])

    def finish(self, request):
        """Questionnaire is complete, so finish up."""

        mess = supergetattr(self, "asker.success_message", None)
        mess and messages.add_message(request, messages.SUCCESS, mess)

        if self.observation:
            self.observation.status = 1
            self.observation.save()

        self.complete = True
        self.save()

    class Meta():
        app_label = 'signalbox'
        verbose_name = "Participant reply"
        verbose_name_plural = "Participant replies"
        permissions = (
            ("can_double_enter", "Can add Data for another person"),
            ("can_resolve_duplicate_replies", "Can resolve duplicate replies"))
        ordering = ['-started']

    def admin_edit_url(self):
        return admin_edit_url(self)

    def __unicode__(self):
        return "Reply: {0}...".format(self.token[:8])
