"""Using tastypie api to expose some model information for admin javascripts."""

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.authentication import Authentication
from tastypie.authorization import DjangoAuthorization
from ask.models import ChoiceSet, Asker, Question

SERIALIZER_FORMATS = ['json',]

class WebAuthentication(Authentication):

    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated():
            return True

    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.username


class AskerResource(ModelResource):
    class Meta:
        queryset = Asker.objects.all()
        authorization = DjangoAuthorization()


class ChoiceSetResource(ModelResource):
    choice_preview = fields.CharField(attribute='choices_as_string')

    class Meta:
        queryset = ChoiceSet.objects.all()
        fields = ['id', 'choice_preview']
        allowed_methods = ['get', 'post']
        filtering = {
            "id": ('exact',),
        }
        serializer = Serializer(formats=SERIALIZER_FORMATS)
        authentication = WebAuthentication()
        authorization = DjangoAuthorization()


