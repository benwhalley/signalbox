import itertools
from datetime import datetime
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.contrib import messages

ALL_MENU_ITEMS = {
    'add_participant': (('Add partcipant'), reverse('new_participant')),
    'add_staff': (('Add new staff member'), reverse('admin:auth_user_add')),
    'followups': (('Participants requiring followups'),
                  reverse('show_followups_outstanding')),
    'textmessage_replies': (('SMS replies'), reverse('admin:signalbox_textmessagecallback_changelist') + "?status=received"),
    'todo': (('Show observations currently due to be sent'), reverse('show_todo')),
    'export': (('Export data'), reverse('export_data')),
    'observations_outstanding': (('Assessments outstanding'), reverse('observations_outstanding')),
}

if settings.USE_VERSIONING:
    ALL_MENU_ITEMS['history'] = (('View revision history'), reverse('check_history'))

ALL_MENU_ITEMS_SORTED = sorted([(k, v) for k, v in ALL_MENU_ITEMS.items()])

PER_GROUP_MENUS = {
    'Researchers': [ALL_MENU_ITEMS[k] for k, v in ALL_MENU_ITEMS_SORTED],
    'Assessors': [ALL_MENU_ITEMS[k] for k in ['followups', 'add_participant', 'observations_outstanding']],
    'Research Assistants': [ALL_MENU_ITEMS[k] for k in
                            ['add_participant', 'add_staff', 'followups', 'todo', 'observations_outstanding']],
    'Clinicians': [ALL_MENU_ITEMS[k] for k in ['todo', 'followups', ]],
    'SuperUsers': [ALL_MENU_ITEMS[k] for k, v in ALL_MENU_ITEMS_SORTED],
}


class AdminMenuMiddleware(object):

    def process_request(self, request):
        if request.user.is_staff:
            supusermenu = (request.user.is_superuser and PER_GROUP_MENUS[
                           'SuperUsers']) or []
            groupmenus = [PER_GROUP_MENUS[i.name]
                          for i in request.user.groups.all()]

            items = sorted(
                set(itertools.chain(
                    *[supusermenu] + groupmenus)
                    )
            )

            request.admin_menu = items
