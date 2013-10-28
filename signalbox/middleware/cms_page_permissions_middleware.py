from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from signalbox.utilities.error_views import render_forbidden_response
from django.db import connection


def recursive_check_login_required(page):
    """Ascend through a page's parents checking whether any need a login to view.

    If a child descends from a login_required page then it is also considered to
    require a login."""
    
    if page.login_required:
        return True
    if page.parent:
        return recursive_check_login_required(page.parent)
    return False


class CmsPagePermissionsMiddleware(object):
    """Alter the behaviour of the 'login required' checkbox in django_cms.

    When this middleware is installed, any page which descends from a page with 'login required'
    will itself require a login.
    """
    
    def process_response(self, request, response):
        """We ensure that users must be staff members (and not just any logged 
        in user)  to see login-protected pages."""

        page = getattr(request, 'current_page', None)
        if page and recursive_check_login_required(page) and not request.user.is_staff:
            return HttpResponseRedirect("/accounts/login?next=%s" % request.path)

        return response
