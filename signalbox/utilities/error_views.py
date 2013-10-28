from django.http import *
from django.template import *
from django.template.loader import get_template
from django.template import RequestContext
    
def render_error_response(message="A system error occured."):
    """Display a 500 error page with a message"""
    t = get_template('500.html')              
    c = Context({'message': message})
    return HttpResponseServerError(t.render(c))

def render_forbidden_response(message="You're not allowed to do that."):
    """Display a 403 error page with a message"""                    
    
    t = get_template('500.html')              
    c = Context({'message': message})
    return HttpResponseForbidden(t.render(c))
