from django.core.management.base import BaseCommand, CommandError
from signalbox.utils import execute_the_todo_list, send_reminders_due_now

class Command(BaseCommand):
    args = ''
    help = 'Sends all observations due.'

    def handle(self, *args, **options):
        todolistresult = execute_the_todo_list()
        self.stdout.write("{}".format([i.id for i, j in todolistresult]))
