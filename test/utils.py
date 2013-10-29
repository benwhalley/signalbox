from django.contrib.auth.models import User
from django.test.client import Client
                                           
from signalbox.models import UserProfile, Membership, Study
from django.contrib.auth.models import User
from signalbox.allocation import allocate




def get_page(url, login=None, *args, **kwargs):
    """Simple wrapper for the test client
    """    
    c = Client()
    if login:
        c.login(username=login['username'], password=login['password'])
    return c.get(url, *args, **kwargs)
        

def post_page(url, postvars, login=None, *args, **kwargs):
    """Simple wrapper for the test client. 
    Accepts url, dictionary of variables to POST, and a dictionary of login
    details (username and password)
    """
    c = Client()                   
    if login:
        c.login(username=login['username'], password=login['password'])
    return c.post(url, postvars, *args, **kwargs)
