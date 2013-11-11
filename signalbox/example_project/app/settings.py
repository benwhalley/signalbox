#!/usr/bin/env python
# -*- coding: utf-8 -*-
import contracts
from django.core.files.storage import FileSystemStorage
from signalbox.configurable_settings import *
from signalbox.utilities.get_env_variable import get_env_variable
from twilio.rest import TwilioRestClient
import imp
import os
import socket
import string
import sys
from signalbox.configurable_settings import *
from signalbox.settings import *


HERE = os.path.realpath(os.path.dirname(__file__))
PROJECT_PATH, SETTINGS_DIR = os.path.split(HERE)
DJANGO_PATH, APP_NAME = os.path.split(PROJECT_PATH)
sys.path.append(APP_NAME)



#####  FILEs  #####

if OFFLINE or TESTING:
    BASE_URL = "/"
    MAIN_STORAGE = 'django.core.files.storage.FileSystemStorage'
    USER_UPLOAD_STORAGE_BACKEND = 'django.core.files.storage.FileSystemStorage'
else:
    DEFAULT_FILE_STORAGE = 'signalbox.s3.MediaRootS3BotoStorage'
    STATICFILES_STORAGE = 'signalbox.s3.StaticRootS3BotoStorage'
    USER_UPLOAD_STORAGE_BACKEND = 'signalbox.s3.PrivateRootS3BotoStorage'
    BASE_URL = 'https://{}.s3.amazonaws.com/'.format(AWS_STORAGE_BUCKET_NAME)
    COMPRESS_STORAGE = STATICFILES_STORAGE
    MAIN_STORAGE = 'storages.backends.s3boto.S3BotoStorage'


MEDIA_ROOT = 'media/'
STATIC_ROOT = 'static/'

STATIC_URL = BASE_URL + STATIC_ROOT
MEDIA_URL = BASE_URL + MEDIA_ROOT
ADMIN_MEDIA_PREFIX = BASE_URL + 'static/admin/'


# # django_compressor
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
    'compressor.filters.template.TemplateFilter',
]




##### STANDARD DJANGO STUFF #####
ROOT_URLCONF = 'urls'
SITE_ID = 1
SESSION_ENGINE = "django.contrib.sessions.backends.file"

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',


    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # reversion must go after transaction
    'django.middleware.transaction.TransactionMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'signalbox.middleware.filter_persist_middleware.FilterPersistMiddleware',
    'signalbox.middleware.cms_page_permissions_middleware.CmsPagePermissionsMiddleware',
    'signalbox.middleware.loginformmiddleware.LoginFormMiddleware',
    'signalbox.middleware.adminmenumiddleware.AdminMenuMiddleware',
    'signalbox.middleware.permissiondenied.PermissionDeniedToLoginMiddleware',
    'signalbox.middleware.error_messages_middleware.ErrorMessagesMiddleware',
    "djangosecure.middleware.SecurityMiddleware",
    'django.middleware.locale.LocaleMiddleware',
)

if ALLOW_IMPERSONATION:
    print >> sys.stderr, "WARNING: Allowing impersonation... make sure this is not left on permanently."
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('signalbox.middleware.impersonatemiddleware.ImpersonateMiddleware', )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)


INSTALLED_APPS = [
    'ask',
    'twiliobox',
    'djangosecure',
    'signalbox',
    'django.contrib.auth',
    'django.contrib.redirects',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.markup',
    'django.contrib.humanize',
    'django_admin_bootstrapped',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'cms',
    'cmsmenu_redirect',
    'registration',
    'south',
    'mptt',
    USE_VERSIONING and 'reversion' or None,
    'django_extensions',
    'menus',
    'sekizai',
    'selectable',
    'storages',
    'cms.plugins.picture',
    'cms.plugins.file',
    'cms.plugins.snippet',
    'cmsplugin_simple_markdown',
    'compressor',
    'floppyforms',
    'bootstrap-pagination',
    'kronos',
    'gunicorn',
]
# filter out conditionally-skipped apps (which create None's)
INSTALLED_APPS = filter(bool, INSTALLED_APPS)

TEMPLATE_LOADERS = (
    'apptemplates.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

# caching enabled because floppyforms is slow otherwise; disable for development
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),
)

# turn off template caching/debugging in debug environment
TEMPLATE_DEBUG = DEBUG
if DEBUG:
    TEMPLATE_LOADERS = TEMPLATE_LOADERS[0][1]

# turn of contracts checking in production
if not DEBUG:
    contracts.disable_all()



# REGISTRATION #
AUTH_PROFILE_MODULE = 'signalbox.UserProfile'

# cron jobs for scheduled tasks
KRONOS_MANAGE = os.path.join(DJANGO_PATH, "app/manage.py")

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/accounts/profile/",
}


LANGUAGE_CODE='en-uk'
TIME_ZONE = 'Europe/London'
USE_I18N = False
USE_L10N = False




##### EMAIL #####

EMAIL_HOST = get_env_variable('EMAIL_HOST', required=False, default='localhost')
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', default="465", required=False))
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', required=EMAIL_HOST != "localhost")
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', required=EMAIL_HOST != "localhost")

if EMAIL_HOST == "localhost" and EMAIL_PORT != 25 and get_env_variable('DEBUG', int_to_bool=True, required=False, default=False):
    EMAIL_PORT = 25
    print >> sys.stderr, "Resetting EMAIL_PORT to 25 because EMAIL_HOST is localhost"





##### CMS #####

PLACEHOLDER_FRONTEND_EDITING = True
SOUTH_TESTS_MIGRATE = False
CMS_REDIRECTS=True

CMS_TEMPLATES = (
    ('base.html', 'base'),
    ('home.html', 'home'),
    ('two.html', 'two'),
)

LANGUAGES = (
    ('en-uk', 'English'),
)

CMS_LANGUAGES = {
        1: [
            {
                'code': 'en-uk',
                'name': 'English',
                'public': True,
                'hide_untranslated': True,
                'redirect_on_fallback':False,
            },
        ],
        'default': {
            'fallbacks': ['en-uk',],
            'public': False,
            'redirect_on_fallback':True,
            'hide_untranslated': False,
        }
    }


LOGGING = {
    'version': 1,
    'formatters': {
    'verbose': {
        'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    },
        'simple': {
        'format': '%(levelname)s %(message)s'
        },
    },
'handlers': {
    'null': {
        'level': 'DEBUG',
        'class': 'django.utils.log.NullHandler',
    },
    'console': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'simple'
    },
},
'loggers': {
    'django': {
        'handlers': ['null'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'signalbox': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    }
}
}
