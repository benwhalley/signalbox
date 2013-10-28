import urlparse
from signalbox.exceptions import SuspiciousActivityException

def sanitise_user_supplied_redirect(request, redirect_to):
    """Make sure users can't add ?success_url=http://nastyurl.com to redirects.

    Borrowed from https://github.com/django/django/blob/master/django/contrib/auth/views.py
    """

    netloc = urlparse.urlparse(redirect_to)[1]
    if netloc and (netloc != request.get_host()):
        raise SuspiciousActivityException("Suspicious redirect spotted.")
    return redirect_to
