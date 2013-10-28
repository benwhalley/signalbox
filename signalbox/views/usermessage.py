from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django import http
from django.template import RequestContext, Context, Template, loader
from django.contrib.auth.decorators import login_required, permission_required

from django import forms
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib import messages

from django_fsm.db.fields.fsmfield import TransitionNotAllowed

from django.conf import settings
from django.contrib.auth.models import User    

from signalbox.models import *
from signalbox.decorators import group_required

from signalbox.forms import UserMessageForm
import selectable.forms as selectable




@group_required(['Researchers', 'Clinicians', 'Assessors', 'Research Assistants' ])
def send_usermessage(request, username=None, message_type='Email'):
    """Send a usermessage to a specified User and keep a record."""
    
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = None
    
    form = UserMessageForm(request.POST or None, 
        initial={'message_to':user, 'message_type':message_type,})
    
    if request.POST and form.is_valid():
        try:
            usermessage = form.save(commit=False)             
            usermessage.message_from = request.user
            result = usermessage.send()
            messages.add_message(request, messages.INFO, "Message sent.")
            return http.HttpResponseRedirect(reverse('participant_overview', args=(usermessage.message_to.id,) ))
        except Exception, e:
            messages.add_message(request, messages.WARNING, "Message not sent: " + str(e))
    
    return render_to_response('manage/user_message.html', {'form':form}, RequestContext(request))
    
    


