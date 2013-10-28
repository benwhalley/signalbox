from __future__ import unicode_literals


from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from django.db import models
from django.conf import settings
from signalbox.utilities.djangobits import supergetattr

def upload_file_name(instance, filename):
    return '/'.join(['userdata', instance.reply.token, filename])


class Answer(models.Model):
    """Stores user questionnaire data."""

    def __iter__(self):
        for i in self._meta.get_all_field_names():
            yield (i, getattr(self, i))

    def __contains__(self, x):
        return x in getattr(self, 'answer')

    question = models.ForeignKey('ask.Question', blank=True, null=True,
        on_delete=models.PROTECT,
        help_text='The question this answer refers to')

    page = models.ForeignKey('ask.AskPage', blank=True, null=True,
        help_text='The page this question was displayed on', on_delete=models.PROTECT)

    other_variable_name = models.CharField(max_length=256, blank=True, null=True)

    choices = models.TextField(blank=True, null=True,
        help_text="""JSON representation of the options the user could select from,
        at the time the answer was saved.""")

    answer = models.TextField(blank=True, null=True)

    upload = models.FileField(blank=True, null=True,
        storage=settings.USER_UPLOAD_STORAGE_BACKEND,
        upload_to=upload_file_name)

    reply = models.ForeignKey('signalbox.Reply', blank=True, null=True)

    last_modified = models.DateTimeField(auto_now=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)

    meta = models.TextField(blank=True, null=True,
        help_text="""Additional data as python dict serialised to JSON.""")

    def mapped_score(self):
        """Return mapped score; leave answer unchanged if no map found."""
        return self.question.score_mapping and \
            self.question.score_mapping.get(self.answer, self.answer) or self.answer

    def participant(self):
        """Return the user to whom the answer relates (maybe not the user who entered it)."""
        return self.reply.observation.dyad.user

    @property
    def study(self):
        """Return the study this Answer was made in response to."""

        return self.reply.observation.dyad.study

    def variable_name(self):
        if self.question:
            return self.question.variable_name
        else:
            return self.other_variable_name

    def possible_choices_json(self):
        return self.question and self.question.choices_as_json()

    def choice_label(self):
        """Returns the label of the original Choice object selected."""

        if not self.question:
            return self.answer

        def _get_label(number):
            try:
                return [j for i, j in self.question.choices() if i == int(self.answer)][0]
            except:
                return None

        return _get_label(self.answer) or self.answer

    def __unicode__(self):
        return smart_text("{} (page {}): {}".format(self.variable_name(), supergetattr(self, "page.id", None), smart_text(self.answer)[:80]))

    class Meta:
        permissions = (
            ("can_view_screening", "Can see responses made to screening instruments"),
        )
        verbose_name_plural = "user answers"
        ordering = ['last_modified']
        unique_together = (['other_variable_name', 'reply', 'page'], ['question', 'reply', 'page'])
        app_label = "signalbox"
