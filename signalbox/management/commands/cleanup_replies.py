from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from signalbox.models.reply import Reply
from django.utils import timezone
from datetime import timedelta

DAYSDELAY = 7

class Command(BaseCommand):
    args = ''
    help = 'Cleanup empty replies after a delay.'

    def handle(self, *args, **options):
        oldemptyreplies = Reply.objects.annotate(
        	num_answers=Count('answer')).exclude(
        	num_answers__gt=0).filter(
        	started__lt=timezone.now()-timedelta(days=DAYSDELAY)
        )
        if oldemptyreplies:
        	print("{}  Deleting Reply IDs {}".format(timezone.now(), [i.id for i in oldemptyreplies]), file=self.stdout)
        	oldemptyreplies.delete()

