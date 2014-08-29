Installation
============================================



To run Signalbox you will need some kind of Unix with python 2.7 available. Ubuntu 12.04 LTS is currently recommended, but OS X is fine too for development.

To get up and running quickly, the easiest way is currently to use Heroku_ . Heroku have a free plan which is capable enough for even quite large studies, although self-hosting is also straightforward.





Prerequisites
----------------

For hosted installations, you just need python, and pip.

For local development, on Ubuntu 12.04, you can install everything you need for a development machine like this::

	sudo apt-get install -y python-dev postgresql-server-dev-9.1 libjpeg-dev virtualenvwrapper libmagic-dev git mercurial zlib1g-dev libfreetype6 libfreetype6-dev
	export WORKON_HOME=~/Envs
	mkdir -p $WORKON_HOME
	source /usr/local/bin/virtualenvwrapper.sh




Hosted installation on Heroku
--------------------------------

To get Signalbox running on Heroku's free plan (which is ideal for normal sized studies), you first need to:

1. Sign up for an account with Heroku (https://devcenter.heroku.com/articles/quickstart) and install their command line tool. You should upload your keys to the server to avoid having to repeatedly type your password:

	heroku keys:add

2. Optionally, if you want to upload images or other media for studies or questionnaires, sign up with Amazon for an S3 storage account (uploaded image files cannot be kept on heroku; see http://aws.amazon.com).

3. Optionally, if you plan to send email, obtain the details  (host, username, password) for an SMTP email server you will use. Amazon's 'simple email service', SES, is good: http://aws.amazon.com/ses/

4. Optionally, if you plan on using interactive telephone calls or SMS, sign up with Twilio and make a note of your secret ID and key: https://www.twilio.com.


Installation
~~~~~~~~~~~~~~~~~

Install the heroku command line program and authenticate::

	wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
	ssh-keygen
	heroku keys:add


Clone the example project::

	git clone GITHUBREPO newname
	cd newname
	pip install -r requirements.txt


The run the install script::

	heroku_install_signalbox

At this point, your installation should be up and running on heroku::

	heroku open

But you need to create the first user to login to the admin site::

	heroku run app/manage.py createsuperuser


Scheduled tasks
~~~~~~~~~~~~~~~~~
Remember to add a scheduled task to send observations via the heroku control panel. The frequency is up to you - polling more often can cost more in dyno time if it overruns the free quota (but not much), but you'll want to add scheduled tasks for these scripts::

	app/manage.py send
	app/manage.py remind

If adding through cron on your own server remember to make sure the python used has signalbox in it's path (i.e. activate the virtualenv first).



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



Version control
~~~~~~~~~~~~~~~~~

Signalbox can use ``django_reversion`` to keep track of changes to Answer, Reply and Observation objects to provide an audit trail for a trial. It's not enabled by default, but to turn it on you can set an environment variable::

	heroku config:set USE_VERSIONING=1




Local install for development
---------------------------------

Once you have Signalbox installed in a virtualenv and a hosted instance running, it's easy to start hacking on it locally to update templates etc.

First make a database with postgres (for development, allow the local user all permissions).

	createdb sbox

Then update the DATABASE_URL environment variable to match your new database. If everything works, open http://127.0.0.1:8000/admin  to view the admin site on your development machine.

Make changes in the local repo, commit them and then::

	git push heroku master



Browser compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The front-end (participant facing pages) should work in almost all browsers, including IE7.

The admin interface works best in a recent webkit browser (Safari or Chrome) but will largely function in IE7 (although the menus are slightly broken, they are usable). Everything will work properly in IE8 onwards.

.. note:: It's recommended to use Chrome-Frame if IE7 is the only available browser. See: `<https://developers.google.com/chrome/chrome-frame/>`_

.. warning:: Check everything works in your target browsers early in the trial setup. The health services and large firms have some weird and wonderful stuff deployed.




Custom domain names
~~~~~~~~~~~~~~~~~~~~~~~

You can add your own domain name to the app, but you will need to update the ALLOWED_HOSTS environment variable. See `<https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts>`_ and `<https://devcenter.heroku.com/articles/config-vars>`_.


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

