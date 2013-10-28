"""Classes used by django-selectable for lookups."""

from django.http import HttpResponseForbidden

from django.contrib.auth import get_user_model
User = get_user_model()

from django.db.models import Q

from selectable.base import ModelLookup
from selectable import registry

from models import Membership, Observation


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


registry.registry.register(UserLookup)
registry.registry.register(MembershipLookup)
