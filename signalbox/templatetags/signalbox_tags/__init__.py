from django import template

register = template.Library()

from django.core.urlresolvers import reverse
from signalbox.decorators import _is_in_group
from signalbox.forms import FindParticipantForm
from signalbox.models import Reply

#Django template custom math filters
#Ref : https://code.djangoproject.com/ticket/361
register = template.Library()

def mult(value, arg):
    "Multiplies the arg and the value"
    return int(value) * int(arg)

def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)

def div(value, arg):
    "Divides the value by the arg"
    return int(value) / int(arg)

register.filter('mult', mult)
register.filter('sub', sub)
register.filter('div', div)



def ad_hoc_scripts(context, participant):
    """Shows ad hoc scripts which this user is allowed to see."""
    user = context['user']

    # TODO write a new manager on Script object to restrict access if will
    # break blind
    everything = [(m, m.study.ad_hoc_scripts.all(), m.study.ad_hoc_askers.all()) for m in participant.membership_set.all()]
    justmemswithscroptoraskers = [(m, s, a) for m, s, a in everything if s or a]
    return justmemswithscroptoraskers

register.assignment_tag(takes_context=True)(ad_hoc_scripts)



def anonymous_asker_url(context, asker):
    """Creates anonymous participation url"""

    request = context['request']
    return request.build_absolute_uri(asker.get_anonymous_url(request))

register.assignment_tag(takes_context=True)(anonymous_asker_url)


def anonymous_data_url(context, asker):
    """Creates anonymous data download url"""
    request = context['request']
    return request.build_absolute_uri(
        reverse('export_anonymous_asker_data', kwargs={'token': asker.anonymous_download_token}
    ))

register.assignment_tag(takes_context=True)(anonymous_data_url)


@register.inclusion_tag('admin/signalbox/_fragments/_visible_replies.html', takes_context=True)
def replies(context, participant=None):

    authorised = Reply.objects.authorised(
        user=context['request'].user).order_by('observation__due')

    if participant:
        authorised = authorised.filter(observation__dyad__user=participant)

    return {
        'replies': authorised
    }


@register.assignment_tag(takes_context=True)
def memberships(context, participant=None):
    from signalbox.models import Membership
    authorised = Membership.objects.authorised(user=context['request'].user)
    if participant:
        authorised = authorised.filter(user=participant)

    return authorised


@register.inclusion_tag('admin/signalbox/_fragments/_find_participant.html', takes_context=True)
def find_participant(context):

    find_participant_form = FindParticipantForm()

    return {
        'find_participant_form': find_participant_form
    }
