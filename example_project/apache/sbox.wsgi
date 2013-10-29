# See http://blog.dscpl.com.au/2010/03/improved-wsgi-script-for-use-with.html

import os, sys
import site


# Setting Environment vars in python

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_PATH =  os.path.join(HERE, "../../")
APP_PATH =  os.path.join(PROJECT_PATH, "sbox")
SITE_PACKAGES = os.path.join(PROJECT_PATH, "v/lib/python2.7/site-packages")

# Check that virtualenv exists
assert os.path.isdir(SITE_PACKAGES)

site.addsitedir(SITE_PACKAGES)
sys.path.append(PROJECT_PATH)
sys.path.insert(0, APP_PATH)
sys.path.insert(0, os.path.join(APP_PATH, 'settings'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sbox.settings'


import settings

import django.core.management
django.core.management.setup_environ(settings)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
