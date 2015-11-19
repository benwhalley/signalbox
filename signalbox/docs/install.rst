Installation
============================================


There are two main ways to use Signalbox: install it on your own server, or use the automated installer to set up a free instance running on Heroku.






Free hosted installation on Heroku
-----------------------------------

It's easy to get Signalbox running on Heroku's free plan (which is ideal for normal sized studies). [Instructions are given on the main Signalbox project site](http://www.thesignalbox.net/deploy/).


Scheduled tasks
~~~~~~~~~~~~~~~~~
Remember to add a scheduled task to send observations via the heroku control panel. The frequency is up to you - polling more often can cost more in dyno time if it overruns the free quota (but not much), but you'll want to add scheduled tasks for these scripts::

	app/manage.py send
	app/manage.py remind

If adding through cron on your own server remember to make sure the python used has signalbox in it's path (i.e. activate the virtualenv first).



Custom domain names
~~~~~~~~~~~~~~~~~~~~~~~

You can add your own domain name to the app, but you will need to update the ALLOWED_HOSTS environment variable. See `<https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts>`_ and `<https://devcenter.heroku.com/articles/config-vars>`_.






Running it yourself
--------------------

If you know what you're doing with Django already, SignalBox is available as a pluggable application, installable via pip (`pip install signalbox`). You might want to study the [example app here](http://github.com/puterleat/signalbox-example-project/tree/master) to check some of the configuration options.



Prerequisites
----------------

To run Signalbox you will need some kind of Unix with python 2.7 available. Ubuntu 14 LTS is currently recommended, but OS X is fine too for development.

For local development, on Ubuntu 12.04, you can install everything you need for a development machine like this::

    sudo apt-get install -y python-dev postgresql-server-dev-9.1 libjpeg-dev virtualenvwrapper libmagic-dev git mercurial zlib1g-dev libfreetype6 libfreetype6-dev
    export WORKON_HOME=~/Envs
    mkdir -p $WORKON_HOME
    source /usr/local/bin/virtualenvwrapper.sh



Customising your own or a Heroku instance
-------------------------------------------


Environment variables
~~~~~~~~~~~~~~~~~~~~~~

Note that all settings, API keys, and passwords are stored in environment variables (see http://www.12factor.net/config).

Environment variables can be se using::

    heroku config:set VAR=SOMEVALUE


The key ones you will need to set are::


    AWS_STORAGE_BUCKET_NAME
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

    TWILIO_ID
    TWILIO_TOKEN

    EMAIL_HOST
    EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD


Others are listed below for reference.



Notifications
~~~~~~~~~~~~~~~~~

::
	DATA_ADMINS

A string of space-separated email addresses to be sent notifications when anonymous questionnaires
are completed.





Version control
~~~~~~~~~~~~~~~~~

Signalbox can use ``django_reversion`` to keep track of changes to Answer, Reply and Observation objects to provide an audit trail for a trial. It's not enabled by default, but to turn it on you can set an environment variable::

    heroku config:set USE_VERSIONING=1





Performance and Caching
~~~~~~~~~~~~~~~~~~~~~~~~

We strongly recommend you use [django-cachalot](http://django-cachalot.readthedocs.org/en/latest/) in your porject (i.e. as an INSTALLED_APPLICATION). Many views are currently not optimised to minimise the number of database queries, and without caching performance will be poor.


::
	CONTRACTS_ENABLED

In addition, ensuring the environment variable `CONTRACTS_ENABLED` is `0` is necessary in production (this is the default) to turn of pycontracts checking.




Browser compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The front-end (participant facing pages) should work in almost all browsers, including IE7.

The admin interface works best in a recent webkit browser (Safari or Chrome) but will largely function in IE7 (although the menus are slightly broken, they are usable). Everything will work properly in IE8 onwards.

.. note:: It's recommended to use Chrome-Frame if IE7 is the only available browser. See: `<https://developers.google.com/chrome/chrome-frame/>`_

.. warning:: Check everything works in your target browsers early in the trial setup. The health services and large firms have some weird and wonderful stuff deployed.






Reference for all user-configurable environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Each of these is loaded from an environment variable by signalbox.configurable_settings.py, and some are documented there::


	DB_URL default: postgres://localhost/sbox

	LOGIN_FROM_OBSERVATION_TOKEN
	SHOW_USER_CURRENT_STUDIES
	DEFAULT_USER_PROFILE_FIELDS

	DEBUG

	AWS_STORAGE_BUCKET_NAME
	COMPRESS_ENABLED
	AWS_QUERYSTRING_AUTH

	SECRET_KEY
	AWS_ACCESS_KEY_ID
	AWS_SECRET_ACCESS_KEY
	TWILIO_ID
	TWILIO_TOKEN

	ALLOWED_HOSTS
	SESSION_COOKIE_HTTPONLY
	SECURE_BROWSER_XSS_FILTER
	SECURE_CONTENT_TYPE_NOSNIFF
	SECURE_SSL_REDIRECT
	SESSION_COOKIE_AGE
	SESSION_SAVE_EVERY_REQUEST
	SESSION_EXPIRE_AT_BROWSER_CLOSE

	SESSION_COOKIE_SECURE=False

	USE_VERSIONING=False







.. _Twilio: http://twilio.com

