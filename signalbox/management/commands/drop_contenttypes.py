from django.core.management.base import NoArgsCommand
from django.contrib.sessions.models import Session


class Command(NoArgsCommand):  # pragma: no cover
    help = """Deletes all session data.
    """

    def handle_noargs(self, *args, **options):
        Session.objects.all().delete()
        return "Deleted all sessions.\n"
