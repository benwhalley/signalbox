"""
Adapted from http://djangosnippets.org/snippets/1392/

"""

from django.http import HttpResponseRedirect
from signalbox.utilities.sanitise_redirects import sanitise_user_supplied_redirect


class AdminRedirectMiddleware:
    """ allows you to customize redirects with the GET line in the admin """

    def process_response(self, request, response):
        try:
            request.session["next"] = request.session.get("next", [])
        except AttributeError:
            return response

        # save redirects if given
        nxt = request.GET.get("next", None)
        if nxt:
            if request.method == "GET":
                if nxt not in request.session["next"]:
                    request.session["next"].append(sanitise_user_supplied_redirect(request, nxt) )
                    # don't let the queue grow too long
                    request.session["next"] = request.session["next"][-3:]
                    return response
        else:
            # request.session["next"] = []
            return response

        # apply redirects
        if request.session["next"] \
        and type(response) == HttpResponseRedirect \
        and request.path.startswith("/admin/"):
            url = request.session["next"].pop()
            return HttpResponseRedirect(url)
        return response
