from registration.backends.simple import SimpleBackend


class SignalboxRegistrationBackend(SimpleBackend):
    def post_registration_redirect(request, user):
        return "/"
