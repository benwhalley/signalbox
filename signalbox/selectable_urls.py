from django.conf.urls import *

from selectable import registry
from selectable import views

registry.autodiscover()

urlpatterns = [
    url(r'^(?P<lookup_name>[-\w]+)/$', views.get_lookup, name="selectable-lookup"),
]
