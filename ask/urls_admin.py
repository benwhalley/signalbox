from ask.models import Asker
from ask.views import preview_asker, show_page, start_anonymous_survey
from ask.views import print_asker, show_codebook, preview_questions, bulk_add_questions
from ask.views.asker_text_editing import edit_asker_as_text
from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView
from django.views.generic.detail import DetailView
from signalbox.decorators import group_required
from signalbox.views.replies import *


# ADMIN PATTERNS

urlpatterns = patterns('',

    url(r'^asker/(?P<asker_id>\d+)/text/$', edit_asker_as_text,
        name="edit_asker_as_text"),

    url(r'^question/add/multiple/$', bulk_add_questions, name="bulk_add_questions"),
    url(r'^asker/(?P<asker_id>\d+)/codebook/$', show_codebook,
        name="show_codebook",),
    url(r'^asker/(?P<asker_id>\d+)/print/$', print_asker,
        name="print_asker",),
    url(r'^preview/questions/(?P<ids>[\w,]+)/$', preview_questions, name="preview_questions"),
    url(r'asker/(?P<pk>\d+)/export/$',
            group_required(['Researchers', 'Research Assistants',])(
                DetailView.as_view(
                    model=Asker, template_name="admin/ask/asker/asker_export.html"
                )
            ),
            name="export_asker"),
)


