from django.template import RequestContext
from django.shortcuts import render_to_response
from signalbox.exceptions import SignalBoxException

class ErrorMessagesMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, SignalBoxException):
            return render_to_response('error.html', {'exception': exception}, context_instance=RequestContext(request))
