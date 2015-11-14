import itertools
from collections import OrderedDict
from datetime import datetime
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.contrib import messages

TASKS = (
    ('export', (('Export data'), reverse('export_data'))),
    ('add_participant', (('New partcipant'), reverse('new_participant'))),
    ('add_staff', (('New staff member'), reverse('admin:auth_user_add'))),
)

REPORTS = (
    ('followups', (('Participants requiring followups'), reverse('show_followups_outstanding'))),
    ('textmessage_replies', (('SMS replies'),
        reverse('admin:signalbox_textmessagecallback_changelist') + "?status=received")),
    ('todo', (('Observations currently due to be sent'), reverse('show_todo'))),
    ('observations_outstanding', (('Assessments outstanding'), reverse('observations_outstanding'))),
)

if settings.USE_VERSIONING:
    REPORTS = REPORTS + (('view history', (('View revision history'), reverse('check_history'))), )

ADMIN_MENU = (('Tasks', TASKS), ('Reports', REPORTS))

PER_GROUP_ITEMS = {
    'Researchers': list(itertools.chain(*[[i for i, j in l] for k, l in ADMIN_MENU])),
    'SuperUsers': list(itertools.chain(*[[i for i, j in l] for k, l in ADMIN_MENU])),
    'Assessors': ['followups', 'add_participant', 'observations_outstanding'],
    'Research Assistants': ['add_participant', 'add_staff', 'followups', 'todo', 'observations_outstanding'],
    'Clinicians': ['todo', 'followups', ],
}


def _filtermenu(items, menu):
    """Return hierarchical (2 levels) menu items if their key is in l"""
    return [(k, [j for i, j in l if i in items]) for k, l in menu]


PER_GROUP_MENUS = {
    'SuperUsers': _filtermenu(PER_GROUP_ITEMS['SuperUsers'], ADMIN_MENU),
    'Research Assistants': _filtermenu(PER_GROUP_ITEMS['Research Assistants'], ADMIN_MENU),
    'Clinicians': _filtermenu(PER_GROUP_ITEMS['Clinicians'], ADMIN_MENU),
    'Researchers': _filtermenu(PER_GROUP_ITEMS['Researchers'], ADMIN_MENU),
    'Assessors': _filtermenu(PER_GROUP_ITEMS['Assessors'], ADMIN_MENU),
}


class AdminMenuMiddleware(object):

    def process_request(self, request):
        if request.user.is_staff:
            if request.user.is_superuser:
                menu = PER_GROUP_MENUS['SuperUsers']
            else:
                # what happens if we have multiple groups? or no group?
                try:
                    menu = PER_GROUP_MENUS[request.user.groups.all()[0].name]
                except Exception:
                    menu = {}

            request.admin_menu = menu
