Installation
============================================



To run Signalbox you will need some kind of Unix with python 2.7 available. Ubuntu 12.04 LTS is currently recommended, but OS X is fine too for development.

To get up and running quickly, the easiest way is currently to use Heroku_ . Heroku have a free plan which is capable enough for even quite large studies, although self-hosting is also straightforward.





OS Dependencies
----------------

On Ubuntu 12.04, you can install everything you need for a development machine like this::

	sudo apt-get install -y python-dev postgresql-server-dev-9.1 libjpeg-dev virtualenvwrapper libmagic-dev git mercurial zlib1g-dev libfreetype6 libfreetype6-dev
	export WORKON_HOME=~/Envs
	mkdir -p $WORKON_HOME
	source /usr/local/bin/virtualenvwrapper.sh



Environment variables
-----------------------

Settings, API keys and passwords are stored in environment variables (see http://www.12factor.net/config).
There are setup scripts (see below) to help store this. You need to edit the CONFIG_REQUIRD.json and CONFIG_OPTIONAL.json files to get started.



Local install
---------------

First make a database with postgres (for development, allow the local user permissions). Then use the included setup_signalbox command to make an example project (note, you can do all this manually, just look at the script and at settings.py in the example project)::
	
	createdb sbox
	setup_signalbox
	
If everything works, open http://127.0.0.1:8000/admin  to view the admin site on your development machine.



Hosted installation
--------------------

To get it running on Heroku's free plan (which is ideal for normal sized studies), you first need to:

1. Sign up for an account with Heroku (https://devcenter.heroku.com/articles/quickstart) and install their command line tool.
 
2. Sign up with Amazon for an S3 storage account (this to host the static image files which cannot be kept on heroku). See http://aws.amazon.com. During the setup process you will need to enter your secret AWS ID and key, but this is not saved on the local machine.


You need to add this information to the CONFIG_REQUIRD.json. Optionally, you may also want to:

3. Obtain the details  (host, username, password) for an SMTP email server you will use. Amazon's 'simple email service', SES, is good: http://aws.amazon.com/ses/

4. If you plan on using interactive telephone calls, sign up with Twilio and make a note of your secret ID and key: https://www.twilio.com.


Then add these settings to CONFIG_OPTIONAL.json. Once done, cd INSIDE the NEW directory created above run these commands::
	
	wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
	ssh-keygen
	heroku keys:add
	
	git init; git add -A; git commit -a -m "initial commit"
	signalbox_make_heroku_app
	signalbox_make_s3_bucket
	signalbox_configure_heroku
	
	git push heroku master
	heroku run app/manage.py syncdb --all --noinput
	heroku run app/manage.py collectstatic --noinput
	heroku apps:open	


Remember to add a scheduled task to send observations via the heroku control panel. The frequency is up to you - polling more often can cost more in dyno time if it overruns the free quota (but not much), but you'll want to add scheduled tasks for these scripts::

	app/manage.py runtask send
	app/manage.py runtask remind
	app/manage.py cleanup
	

	
Finally, when you are happy things are working, be sure to turn DEBUG mode off to avoid security problems:

	heroku config:set DEBUG=0
	


To create test users of each of the different roles for demonstration purposes::

    app/manage.py make_dummy_users






Version control
~~~~~~~~~~~~~~~~~

Signalbox can use ``django_reversion`` to keep track of changes to Answer, Reply and Observation objects to provide an audit trail for a trial. It's not enabled by default, but to turn it on you can set an environment variable:

::
    export USE_VERSIONING=1

or::
	
	heroku config:set USE_VERSIONING=1
	
	


Browser compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The front-end (participant facing pages) should work in almost all browsers, including IE7.

The admin interface works best in a recent webkit browser (Safari or Chrome) but will largely function in IE7 (although the menus are slightly broken, they are usable). Everything will work properly in IE8 onwards.

.. note:: It's recommended to use Chrome-Frame if IE7 is the only available browser. See: `<https://developers.google.com/chrome/chrome-frame/>`_

.. warning:: Check everything works in your target browsers early in the trial setup. The health services and large firms have some weird and wonderful stuff deployed.







Reference for all user-configurable environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Each of these is loaded from an environment variable by signalbox.configurable_settings.py, and some are documented there. XXX Add more details here.


DB_URL default: postgres://localhost/sbox

LOGIN_FROM_OBSERVATION_TOKEN
SHOW_USER_CURRENT_STUDIES

DEBUG
OFFLINE

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
 
ALLOW_IMPERSONATION
USE_VERSIONING







.. _Twilio: http://twilio.com

