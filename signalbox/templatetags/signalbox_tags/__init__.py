from django import template

register = template.Library()

from signalbox.decorators import _is_in_group
from signalbox.forms import FindParticipantForm
from signalbox.models import Reply


def ad_hoc_scripts(context, participant):
    """Shows ad hoc scripts which this user is allowed to see."""
    user = context['user']

    # TODO write a new manager on Script object to restrict access if will
    # break blind
    return [(m, m.study.ad_hoc_scripts.all()) for m in participant.membership_set.all()]

register.assignment_tag(takes_context=True)(ad_hoc_scripts)


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
