from django import http
from django.contrib.auth import models
from django.contrib import messages

class ImpersonateMiddleware(object):
    def process_request(self, request):
        impersonate_user = request.GET.get('__impersonate', None)
        if getattr(request, 'user', None) and request.user.is_superuser and impersonate_user:
            request.user = models.User.objects.get(username=impersonate_user)
            messages.add_message(request, messages.ERROR,
                "Impersonating {}. DO NOT USE IMPERSONATION FOR ENTERING DATA FOR OTHER USERS.".format(impersonate_user))

    def process_response(self, request, response):
        if getattr(request, 'user', None) and request.user.is_superuser and "__impersonate" in request.GET:
            if isinstance(response, http.HttpResponseRedirect):
                location = response["Location"]
                if "?" in location:
                    location += "&"
                else:
                    location += "?"
                location += "__impersonate=%s" % request.GET["__impersonate"]
                response["Location"] = location
        return response
