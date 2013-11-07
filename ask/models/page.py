from django.db import models
from django.core.urlresolvers import reverse
from signalbox.utilities.linkedinline import admin_edit_url
from question import Question
from signalbox.process import Step


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
    """A grouping of Questions and Instruments, as part of a Questionnaire."""

    def index(self):
        return self.page_number()

    def available(self, reply):
        for step, available in reply.step_availability():
            if self == step:
                return True

    def visible_questions(self, reply):
        return  filter(lambda i: i.showme(reply), self.get_questions())

    def visible_variable_names(self, reply):
        return  [i.variable_name for i in self.visible_questions(reply)]

    def answers(self, reply):
        return reply.answer_set.filter(question__variable_name__in=self.visible_variable_names(reply))

    def validate(self, reply):
        """Checks to see if the page is complete."""
        if reply.entry_method == "page_preview":
            return True
        answers = self.answers(reply)
        return bool(len(answers) >= len(self.visible_variable_names(reply)))

    def all_questions_complete(self, reply):
        if self.questions_which_require_answers() == 0:
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
        pages = list(self.asker.askpage_set.all())
        return pages.index(self)

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

        Rather than simply using a queryset, we build and return a list
        joining together all the questions within included intruments.
        '''

        ordered_questions = []
        for i in self.question_set.all().order_by('order'):
            if "instrument" in i.q_type:
                ins_questions = list(i.display_instrument.question_set.all())
                for k in ins_questions:
                    k.required = i.required
                    k.showif = i.showif
                    k.page = i.page

                ordered_questions.extend(ins_questions)
            else:
                ordered_questions.append(i)

        return ordered_questions

    def questions_to_show(self, reply=None):
        """Return Questions in the page, filtered depending on users past answers in this Reply."""

        qlist = self.get_questions(reply)

        if reply:
            qlist = [q for q in qlist if q.showme(reply) is True]
        return qlist

    def questions_which_require_answers(self):
        return sum([i.response_possible() for i in self.questions_to_show()])

    class Meta:
        verbose_name = "Page"
        ordering = ['order'] # asker display functionality depends on this
        unique_together = ['order', 'asker']
        app_label = "ask"

    def admin_edit_url(self):
        return admin_edit_url(self)

    def __unicode__(self):
        return u"{}: {} (p {})".format(self.asker, self.step_name, self.order)
