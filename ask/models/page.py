# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.db import models
from question import Question
from signalbox.process import Step
import itertools
from signalbox.utilities.linkedinline import admin_edit_url
from signalbox.utilities.djangobits import supergetattr
from contracts import contract

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

    def available(self, reply):
        for step, available in reply.step_availability():
            if self == step:
                return True

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

    asker = models.ForeignKey('Asker')
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

    def progress_pages(self):
        """Returns a tuple with current page and number of pages for use in progress bar.
        """
        return (self.page_number() + 1, self.asker.page_count())

    def percent_complete(self):
        if self.asker.show_progress:
            return int((self.page_number() + 1.0) / self.asker.page_count() * 100)
        return None

    def next_page(self):
        next_pages = self.asker.askpage_set.filter(order__gt=self.order)
        return head(next_pages)

    def prev_page(self):
        prev_pages = self.asker.askpage_set.filter(order__lt=self.order).order_by('-order')
        return head(prev_pages) or self.asker.first_page()

    def get_questions(self, reply=None):
        '''Returns an ordered list of Questions for the page.

        Passing a reply filters using _questions_to_show()
        '''

        if not reply:
            return self.question_set.all().order_by('order')
        else:
            return self._questions_to_show(reply=reply)

    def _questions_to_show(self, reply):
        """Filtered list of questions, based on users past answers in this Reply."""

        mapping_of_answers = {
            supergetattr(i, 'question.variable_name', i.other_variable_name): i.answer
                for i in reply.answer_set.all()
        }
        mapping_of_answers.update({k: v.get('score', None) for k, v in self.summary_scores(reply).items()})
        qlist = self.get_questions()
        return [q for q in qlist if bool(q.show_conditional(mapping_of_answers))]

    @contract
    def questions_which_require_answers(self, reply=None):
        """
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

    def __unicode__(self):
        return u"{}: {} (p {})".format(self.asker, self.step_name, self.order)
