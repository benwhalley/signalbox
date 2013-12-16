# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from signalbox.process import Step
import itertools
from signalbox.utilities.linkedinline import admin_edit_url
from signalbox.utilities.djangobits import supergetattr
from signalbox.custom_contracts import *


def head(iterable):
    """Return the first item in an iterable or None"""
    try:
        return iterable[0]
    except IndexError:
        return None


class AskPageManager(models.Manager):
    def get_by_natural_key(self, slug, order):
        return self.get(asker__slug=slug, order=order)


class AskPage(models.Model, Step):
    """A grouping of Questions, as part of a Questionnaire."""

    def index(self):
        return self.page_number()

    @contract
    def available(self, reply):
        """
        Are we allowed to complete this page now?

        :type reply: is_reply
        :rtype: bool
        """
        for step, available in reply.step_availability():
            if self == step:
                return True
        return False

    def scoresheets(self):
        return set(filter(bool, [i.scoresheet for i in self.get_questions()]))

    def visible_variable_names(self, reply):
        return  [i.variable_name for i in self.get_questions(reply)]

    def answers(self, reply):
        return reply.answer_set.filter(question__variable_name__in=self.visible_variable_names(reply))

    def validate(self, reply):
        """Checks to see if the page is complete."""
        if reply.entry_method == "page_preview":
            return True
        answers = self.answers(reply)
        return bool(len(answers) >= len(self.visible_variable_names(reply)))

    def all_questions_complete(self, reply):
        if self.questions_which_require_answers(reply) == 0:
            return False
        answers = self.answers(reply)
        answers = filter(lambda x: bool(x.answer), answers)
        return bool(len(answers) >= len(self.visible_variable_names(reply)))

    def natural_key(self):
        return (self.asker.slug, self.order)

    asker = models.ForeignKey('ask.Asker')
    order = models.FloatField(default=0)

    submit_button_text = models.CharField(max_length=255, default="""Continue""")
    step_name = models.CharField(max_length=255, null=True, blank=True)

    def name(self):
        return self.step_name or "Page {}".format(self.index() + 1)

    def get_absolute_url(self):
        return reverse('preview_asker',
            kwargs={'asker_id': self.asker.id, 'page_num': self.index()})

    def pages(self):
        return AskPage.objects.filter(asker=self.asker).order_by('order')

    def page_number(self):
        pages = list(itertools.chain(*self.asker.askpage_set.all().values_list('id')))
        return pages.index(self.id)

    def is_last(self):
        return self == list(self.asker.askpage_set.all())[-1]

    @contract
    def progress_pages(self):
        """Returns a tuple with current page and number of pages for use in progress bar.
        :rtype: tuple(int, int)
        """
        return (self.page_number() + 1, self.asker.page_count())

    def next_page(self):
        next_pages = self.asker.askpage_set.filter(order__gt=self.order)
        return head(next_pages)

    def prev_page(self):
        prev_pages = self.asker.askpage_set.filter(order__lt=self.order).order_by('-order')
        return head(prev_pages) or self.asker.first_page()

    @contract
    def get_questions(self, reply=None):
        '''Returns an ordered list of Questions for the page.
        Passing a reply filters using _questions_to_show()
        :rtype: list(is_question)
        '''

        if not reply:
            return list(self.question_set.all().order_by('order'))
        else:
            return self._questions_to_show(reply=reply)

    @contract
    def _questions_to_show(self, reply):
        """Filtered list of questions, based on users past answers in this Reply.
        :type reply: is_reply
        :rtype: list(is_question)
        """

        qlist = self.get_questions()
        answer_mapping = reply.mapping_of_answers_and_scores()
        toshow = [q for q in qlist
            if bool(q.show_conditional(answer_mapping))]
        return toshow

    @contract
    def questions_which_require_answers(self, reply):
        """
        :type reply: is_reply
        :rtype: int
        """
        return sum([i.response_possible() for i in self.get_questions(reply)])

    def summary_scores(self, reply):
        answers = reply.answer_set.all()
        return {i.name: i.compute(answers) for i in self.scoresheets()}

    class Meta:
        verbose_name = "Page"
        ordering = ['order'] # asker display functionality depends on this
        unique_together = ['order', 'asker']
        app_label = "ask"

    def admin_edit_url(self):
        return admin_edit_url(self)

    MARKDOWN_FORMAT = u"\n\n# {}\n"

    def as_markdown(self):
        return self.MARKDOWN_FORMAT.format(self.step_name or "")

    def __unicode__(self):
        return u"{}: {} (p {})".format(self.asker, self.step_name, self.order)
