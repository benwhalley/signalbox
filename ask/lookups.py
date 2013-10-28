"""Classes used by django-selectable for lookups."""

from django.db.models import Q
from django.template.defaultfilters import slugify

from selectable.base import ModelLookup
from selectable import registry

from ask.models import Question, ShowIf


class ShowIfLookup(ModelLookup):
    model = ShowIf


class QuestionLookup(ModelLookup):
    model = Question

    def create_item(self, value):
        question, _ = Question.objects.get_or_create(variable_name=slugify(value),
                                                    text="Edit your new question",
                                                    q_type='instruction')
        return question

    def get_query(self, request, term):
        queryset =  Question.objects.filter(
                            Q(variable_name__icontains=term)
                            | Q(text__icontains=term)
                        )
        return queryset

    def get_item_label(self, item):
        return "%s" % (item.variable_name)

    def get_item_value(self, item):
        return item.text


registry.registry.register(QuestionLookup)
