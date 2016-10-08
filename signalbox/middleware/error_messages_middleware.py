from django.shortcuts import render
from signalbox.exceptions import SignalBoxException

class ErrorMessagesMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, SignalBoxException):
            return render(request, 'error.html', {'exception': exception})
