import magic
import operator
import itertools
import floppyforms
from django import forms
import selectable.forms as selectable

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect, HttpResponse, \
    HttpResponseForbidden, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import FormView

from django.template import Context
from django.template.loader import get_template

from django.contrib.auth.models import User

from django.utils.decorators import method_decorator

from reversion.models import Revision

from signalbox.models import Membership, Observation, Script, Study, Reply, \
    StudyCondition, Answer
from signalbox.models.observation_timing_functions import \
    observations_due_in_window
from signalbox.decorators import group_required
from signalbox.utils import pretty_datetime
from signalbox.allocation import allocate
from signalbox.models.observation_helpers import *

from signalbox.lookups import UserLookup, MembershipLookup
from django.contrib.auth.forms import PasswordResetForm

from django.views.generic.detail import SingleObjectMixin
from download_view import DownloadView

from django.core.exceptions import PermissionDenied
from signalbox.models.naturaltimes import parse_natural_date


class AnswerFileView(SingleObjectMixin, DownloadView):
    model = Answer
    use_xsendfile = False

    def get_object(self, queryset=None):
        obj = super(AnswerFileView, self).get_object()
        if obj.reply in Reply.objects.authorised(user=self.request.user):
            return obj
        else:
            raise PermissionDenied

    def get_contents(self):
        return self.get_object().upload.read()

    def get_mimetype(self):
        return magic.from_buffer(self.get_object().upload.read(1024),
                                 mime=True)

    def get_filename(self):
        return self.get_object().upload.name


def do_outstanding_observations(request):
    from signalbox.cron import send, remind

    return HttpResponse(
        str((send(), remind()))
    )


@group_required(['Researchers', 'Research Assistants'])
def send_password_reset(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = PasswordResetForm({'email': user.email})
    if form.is_valid():
        form.save(email_template_name="auto_password_reset_email.html")
        messages.success(request, "Password reset email sent.")

    return HttpResponseRedirect(reverse('participant_overview',
                                        args=(user.id,)))


class VersionView(ListView):
    model = Revision
    paginate_by = 60

    def get_queryset(self):
        return Revision.objects.filter(user__isnull=False).order_by('-date_created')

    @method_decorator(group_required(['Researchers']))
    def dispatch(self, *args, **kwargs):
        return super(VersionView, self).dispatch(*args, **kwargs)


class CreateMembershipForm(forms.ModelForm):
    """Used to add a participant to a Study."""

    user = selectable.AutoCompleteSelectField(
        label='Type the name of the participant', lookup_class=UserLookup,
        required=True,
    )
    relates_to = selectable.AutoCompleteSelectField(
        label='(Optional) patient to link this membership to:',
        lookup_class=MembershipLookup, required=False,
    )

    date_randomised = forms.DateField(
        help_text="""Format: dd/mm/yyyy""", required=False)

    class Meta:
        model = Membership
        fields = ['user', 'study', 'relates_to', 'date_randomised']


@group_required(['Researchers', 'Clinicians', 'Research Assistants', 'Assessors'])
def add_participant(request, study_id=None, user_id=None):
    data = {}
    if study_id:
        data['study'] = get_object_or_404(Study, id=study_id)
    if user_id:
        data['user'] = get_object_or_404(User, id=user_id)

    form = CreateMembershipForm(request.POST or None, initial=data)

    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('participant_overview',
                                            args=(form.cleaned_data['user'].id,)))
    return render_to_response('admin/signalbox/add_participant.html',
                              {'form': form}, RequestContext(request, {}))


@group_required(['Researchers'])
def randomise_membership(request, membership_id):
    """View to assign Membership to Condition"""

    mem = get_object_or_404(Membership, id=int(membership_id))
    was_allocated = allocate(mem)

    if was_allocated[0] is True:
        messages.success(request, was_allocated[1])
    else:
        messages.error(request, was_allocated[1],)
    return HttpResponseRedirect(reverse('admin:signalbox_membership_change', args=(mem.id,)))


@group_required(['Researchers', ])
def add_observations_for_membership(request, membership_id):
    """Add observations for the Membership based on the Condition they are assigned to"""

    mem = get_object_or_404(Membership, id=int(membership_id))
    if mem.condition:
        if len(mem.observations()) == 0:
            mem.add_observations()
            messages.info(request, "Observations added")
        else:
            messages.warning(request, "Observations already added")
    else:
        messages.warning(
            request, "User not allocated to a study condition yet.")
    return HttpResponseRedirect(reverse('admin:signalbox_membership_change', args=(mem.id,)))


def _preview_message(script, subject, body):
    """This mocks an observation as part of a study etc to preview an email message for a script."""

    participant, new = User.objects.get_or_create(
        first_name='Jon', last_name='Doe', username='jondoe')
    therapist, new = User.objects.get_or_create(
        first_name='Sigmund', last_name='Freud', username='sfreud')
    participant.save(), therapist.save()
    clientstudy = Study(slug='clientstudy', name="CLIENT STUDY")
    therapiststudy = Study(slug='therapiststudy', name="THERAPIST STUDY")
    participantmembership = Membership(study=clientstudy, user=participant)
    therapistmembership = Membership(study=therapiststudy, user=therapist,
                                     relates_to=participantmembership)
    observation = Observation(dyad=therapistmembership, created_by_script=script,
                              token="d5044bcc-a06b-11e1-9c18-0023dfaac8d4")

    subject, message = format_message_content(subject, body, observation)
    [i.delete() for i in [therapist, participant]]

    return (subject, message)


@group_required(['Researchers', ])
@csrf_exempt  # exempt because it's called by jQuery asynchronously
def script_message_preview(request):

    if request.POST:
        script = get_object_or_404(Script, id=request.POST.get('script_id'))
        message = _preview_message(script,
                                   subject=request.POST.get('subject', ""),
                                   body=request.POST.get('body', ""))
        return HttpResponse(message)

    else:
        return HttpResponse("Nothing specified")


@csrf_exempt
@group_required(['Researchers', ])
def preview_timings_as_txt(request):
    templ = get_template("admin/signalbox/_fragments/_preview_time.html")
    syntax = request.POST.get("syntax", "")
    if not syntax:
        raise Http404
    dates = map(parse_natural_date, syntax.splitlines())
    output = templ.render(Context({'object_list': dates}))
    return HttpResponse(output)


@group_required(['Researchers', ])
def preview_timings(request, klass="Study", pk=None):
    '''Creates a preview list of the date/times generated by a schedule

    Hooked up in the admin site, this allows users to check their dateutil
    syntax. Errors are not caught, but this makes it fairly easy to see what
    is thrown by the dateutil module'''

    if klass == "StudyCondition":
        obj = studycondition = get_object_or_404(StudyCondition, id=pk)
        scripts = studycondition.scripts.all()
    elif klass == "Script":
        obj = get_object_or_404(Script, id=pk)
        scripts = [obj]

    datelist = [{'script':script, 'times':
                 script.datetimes_with_natural_syntax()} for script in scripts]
    datelist = itertools.chain(
        *[[(i, j['script']) for i in j['times']] for j in datelist])

    datelist = filter(lambda x: bool(x[0]['datetime']), datelist)
    datelist = sorted(list(datelist), key=operator.itemgetter(0))
    extra = {'dl': datelist, 'object': obj, 'object_type': obj.__class__.__name__}
    return render_to_response('admin/signalbox/rule_preview.html', extra, RequestContext(request))


@group_required(['Researchers', 'Research Assistants'])
def show_todo(request):
    todo_list = observations_due_in_window()
    return render_to_response('admin/signalbox/todo_list.html',
                              {'item_list': todo_list, 'results': []},
                              context_instance=RequestContext(request))


@group_required(['Researchers', ])
def do_todo(request):
    """Do the todo list and output a list of Observations done."""

    todo_list = observations_due_in_window()
    results = [i.do() for i in todo_list]
    for i in results:
        messages.success(request, i)

    return HttpResponseRedirect(reverse('show_todo'))


@group_required(['Researchers', ])
def resolve_double_entry_conflicts(request, study_id=None, observation_id=None):
    """This view will allow study administrators to:

    1. Identify observations where double entry has occured (i.e. 2 replies exist)
    2. Select one of several conflicting replies to be used for analysis by marking it as
    'canonical'

    Replies marked canonical will be preferred if another Reply exists for the same observation
    but has not been tagged.

    No double-entered data will ever be deleted and will always be available for review.

    """

    if not study_id and not observation_id:
        studies = [(i,
                    len(i.unresolved_observations_with_duplicate_replies()),
                    len(i.observations_with_duplicate_replies())) for i in Study.objects.all()]

        studies = sorted(
            [i for i in studies if i[2]], key=lambda a: a[1], reverse=True)

        pagevars = {'studies': studies}
        return render_to_response(
            'admin/signalbox/answer/list_studies_with_duplicates.html', pagevars,
            context_instance=RequestContext(request))

    pagevars = {}
    if study_id:
        pagevars['study'] = get_object_or_404(Study, id=study_id)
        pagevars['with_dupes'] = pagevars[
            'study'].observations_with_duplicate_replies()
        return render_to_response(
            'admin/signalbox/answer/list_duplicates.html', pagevars,
            context_instance=RequestContext(request))

    if observation_id:
        pagevars['observation'] = get_object_or_404(Observation,
                                                    id=observation_id)
        return render_to_response(
            'admin/signalbox/answer/resolve_duplicates.html', pagevars,
            context_instance=RequestContext(request))

    pagevars = {'with_dupes': with_dupes}


@group_required(['Researchers', ])
def mark_reply_as_canonical(request, reply_id, set_to=True, hide_canonical=True):
    """Accept a reply_id and mark this Reply as canonical.

    This function sets all other replies for the Observation as not-canonical.
    See resolve_double_entry_conflicts function for definition of what canonical means.
    """

    reply = get_object_or_404(Reply, id=reply_id)
    for r in reply.observation.reply_set.all():
        r.is_canonical_reply = False
        r.save()
    reply.is_canonical_reply = set_to
    reply.save()

    return resolve_double_entry_conflicts(request, observation_id=reply.observation.id)


@group_required(['Researchers', ])
def resend_observation_signal(request, obs_id,):
    """Does the observation again, ignoring constraints of timeouts etc."""

    observation = get_object_or_404(Observation, id=obs_id)
    if request.user.has_perm('signalbox.can_force_send'):
        result, message = observation.do()
        if result == 1:
            messages.info(request, message)
        else:
            messages.warning(request, message)
    else:
        messages.warning(
            request, "You don't have permission to resend this observation.")

    return HttpResponseRedirect(
        reverse('admin:signalbox_observation_change', args=(str(observation.id),)))


class ObservationView(ListView):
    model = Observation
    paginate_by = 30
    template_name = "admin/signalbox/observation_list.html"

    def get_context_data(self, **kwargs):
        context = super(ObservationView, self).get_context_data(**kwargs)
        if not context.get('title', None):
            membership = get_object_or_404(Membership, pk=self.kwargs['pk'])
            context['title'] = "Observations for: " + str(membership)
            context['membership'] = membership
        return context

    def get_queryset(self):
        return Observation.objects.personalised(
            self.request.user).filter(
                dyad__id=self.kwargs['pk']).order_by('due')


class ReplyUpdateAfterDoubleEntryForm(forms.ModelForm):
    originally_collected_on = floppyforms.DateField(required=False, help_text="""Set this if the
        date that data were entered into the system is not the date
        that the participant originally provided the responses (e.g. when retyping paper data).
        If the participant has just provided this data now, then leave blank. """)

    class Meta:
        model = Reply
        fields = ['originally_collected_on']


class ReplyUpdateAfterDoubleEntry(UpdateView):

    def get_success_url(self):
        return reverse('membership_observations_todo',
                       args=(self.object.observation.dyad.id,))

    def form_valid(self, form):
        messages.success(self.request, "Reply updated.")
        return super(ReplyUpdateAfterDoubleEntry, self).form_valid(form)

    model = Reply
    template_name = "admin/signalbox/check_double_entry.html"
    form_class = ReplyUpdateAfterDoubleEntryForm
