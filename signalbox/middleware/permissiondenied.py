from django.contrib import messages
from django.template import RequestContext, loader
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse

class PermissionDeniedToLoginMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            messages.add_message(request, messages.WARNING, exception)
            return HttpResponseRedirect(reverse('django.contrib.auth.views.login') + '?next=' + request.path)
        return None
