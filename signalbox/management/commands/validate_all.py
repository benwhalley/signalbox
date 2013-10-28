from django.core.management.base import NoArgsCommand
from django.db import connections


class Command(NoArgsCommand):  # pragma: no cover
    help = """Call full_clean on every object in the DB."""

    def handle_noargs(self, *args, **options):
        connection = connections['default']
        tables = connection.introspection.table_names()
        modelclasses = connection.introspection.installed_models(tables)

        for j in modelclasses:
            print j
            for i in j.objects.all():
                try:
                    i.full_clean()
                except Exception as e:
                    print j, i.id, i, e
