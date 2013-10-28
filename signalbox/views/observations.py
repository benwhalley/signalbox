from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, Template
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import *
from django.views.decorators.cache import *
from django.utils.safestring import *
from django.contrib.auth.models import User

from collections import defaultdict

from signalbox.models import *
from signalbox.decorators import group_required
from ask.models import *

from django import forms
# from django.views.generic import list_detail
import django_tables as tables


class ObservationTable(tables.MemoryTable):
    user = tables.Column(verbose_name="Participant")
    due = tables.Column()
    status = tables.Column()
    site = tables.Column()
    ob_type = tables.Column(verbose_name="Type")
    editlink = tables.Column(verbose_name="-", sortable=False)

import selectable.forms as selectable
from signalbox.lookups import UserLookup


# class FilterForm(forms.Form):
#     user = selectable.AutoCompleteSelectField(
#         label='Type the name of the participant', lookup_class=UserLookup, required=False,
#     )
#     studies = forms.ModelMultipleChoiceField(
#         required=False, queryset=Study.objects.all())
#     script_type = forms.ModelMultipleChoiceField(
#         required=False, queryset=ScriptType.objects.all())
#     from_date = forms.DateField(
#         required=False, help_text="Enter day month year")
#     to_date = forms.DateField(required=False, )
#     status = forms.MultipleChoiceField(
#         required=False, choices=settings.STATUS_CHOICES,)
#     sites = forms.ModelMultipleChoiceField(
#         required=False, queryset=StudySite.objects.none())

#     def __init__(self, *args, **kwargs):
#         qs = kwargs.pop('sites')
#         super(FilterForm, self).__init__(*args, **kwargs)
#         self.fields['sites'].queryset = qs


# @group_required(['Researchers', ])
# def list_obs(request):
#     """Filter view to allow administrators to check Observation completions etc."""
#     studies = Study.objects.all()
#     sites = StudySite.objects.all()
#     qset = Observation.objects.filter(dyad__study__in=studies)
#     form = FilterForm(request.GET or None, sites=sites)

#     if form.is_valid():
#         def _add_form_filter(form, field, filt, default):
#             val = form.cleaned_data.get(field) or default
#             if val:
#                 return {filt: val}
#             return {}

#         # These strings are used to match form fields with filter queries to be made.
#         # A default is allowed.
#         filterstrings = (
#             ('status', 'status__in', None),
#             ('user', 'dyad__user', None),
#             ('sites', 'dyad__user__userprofile__site__in', None),
#             ('studies', 'dyad__study__in', None),
#             ('script_type',
#              'created_by_script__script_type__in', None),
#             ('from_date', 'due__gte', None),
#             ('to_date', 'due__lte', None),
#         )
#         filters = {}
#             # create a big dictionary with all the filter parameters in
#         [filters.update(_add_form_filter(form, fie, fil, default)) for fie, fil, default
#             in filterstrings]
#         qset = qset.filter(**filters)  # Now actually do the filtering

#     tabledata = [{
#         'due': i.due, 'user': i.dyad.user,
#         'site': i.dyad.user.get_profile().site,
#         'status': i.status_string(),
#         'ob_type': i.script_type(),
#         'editlink': mark_safe(
#             "<a href='%s'>edit</a>" % reverse('admin:signalbox_observation_change',
#                                                                 args=(str(i.id),)))
#     } for i in qset]

#     observations = ObservationTable(
#         tabledata, order_by=request.GET.get('sort'))

#     return list_detail.object_list(request,
#        queryset=qset,
#        template_name="admin/signalbox/list_obs.html",
#        template_object_name="obs",
#        extra_context={'table': observations,
#                         'qstring': request.GET.urlencode(),
#                         'form': form, 'studies': studies})
