"""Classes used by django-selectable for lookups."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Membership, Observation
from selectable import registry
from selectable.base import ModelLookup
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

class UserLookup(ModelLookup):
    model = User

    def get_query(self, request, q):
        if not request.user.is_staff:
            return HttpResponseForbidden()

        return User.objects.filter(
            Q(first_name__istartswith=q)
            | Q(last_name__istartswith=q)
            | Q(email__icontains=q)
            | Q(username__icontains=q))

    def create_item(self, value):
        try:
            assert len(value) >= 3
            return User.objects.get(username__istartswith=value)
        except Exception:
            return None

    def get_item_label(self, user):
        return user.username

    def get_item_value(self, user):
        return user.username


class MembershipLookup(ModelLookup):
    model = Membership
    search_field = 'user__username__icontains'

    def get_query(self, request, term):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        queryset = Membership.objects.filter(
            Q(user__first_name__istartswith=term)
            | Q(user__last_name__istartswith=term)
            | Q(user__email__icontains=term)
            | Q(user__username__icontains=term)
        )
        return queryset


class ObservationLookup(ModelLookup):
    model = Observation

    def get_query(self, request, term):
        if not request.user.is_staff:
            return HttpResponseForbidden()
        queryset = Observation.objects.filter(
            Q(dyad__user__username__istartswith=term)
            | Q(id__istartswith=term)
        )
        return queryset

    def get_item_label(self, item):
        return "Observation #{} (user:{}, {})".format(item.id, item.dyad.user.username, item.label)

    def get_item_value(self, item):
        return "%s" % (item.id)




registry.registry.register(UserLookup)
registry.registry.register(ObservationLookup)
registry.registry.register(MembershipLookup)
