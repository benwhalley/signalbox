from django.db.models import Q
from datetime import datetime as d
from django.conf.urls.defaults import *
from django.views.generic import ListView, DetailView
from django.views.generic.dates import MonthArchiveView
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from signalbox.views.participants import edit_participant, find_participant
from signalbox.views.front import join_study, user_homepage, MembershipDetail
from signalbox.models.study import study



class ProfileApphook(CMSApp):
    name = _("User profile")
    urls = [patterns('',
        url(r'^$', user_homepage, name='user_homepage'),
    ),]
apphook_pool.register(ProfileApphook)


class EditParticipantApphook(CMSApp):
    name = _("Add or edit a new participant")
    urls = [patterns('',
        url(r'^(?P<id>\d+)?/?$', edit_participant, {}, 'edit_participant'),
        url(r'^$', edit_participant, {}, 'edit_participant'),
    ),]
apphook_pool.register(EditParticipantApphook)



class ParticipantApphook(CMSApp):
    name = _("Find participant")
    urls = [patterns('',
        url(r'^$', find_participant, {}, 'find_participant'),
    ),]
apphook_pool.register(ParticipantApphook)

