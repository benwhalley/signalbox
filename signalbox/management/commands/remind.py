from django.core.management.base import BaseCommand, CommandError

from signalbox.utils import send_reminders_due_now

class Command(BaseCommand):
    args = ''
    help = 'Sends all reminders due.'

    def handle(self, *args, **options):
        reminderlistresult = send_reminders_due_now()
        self.stdout.write("{}".format([i.id for i, j in reminderlistresult]))
