Installation
============================================



To run Signalbox you will need some kind of Unix with python 2.7 available. Ubuntu 12.04 LTS is currently recommended, but OS X is fine too for development.

To get up and running quickly, the easiest way is currently to use Heroku_ . Heroku have a free plan which is capable enough for even quite large studies, although self-hosting is also straightforward.




Using Vagrant
~~~~~~~~~~~~~~~~
In future we might think about using... https://github.com/torchbox/vagrant-django-base


To create a local development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Install the following packages (e.g. using ``apt-get`` or ``brew`` on OS X)::

    virtualenvwrapper
    libmagic


Make a virtual environment, activate it and install python dependencies::

    mkvirtualenv sbox
    workon sbox
    pip install -r requirements.txt


..note:: For more or pip and virtualenv see http://www.saltycrane.com/blog/2009/05/notes-using-pip-and-virtualenv-django/



Add some variables to your shell (e.g. via `.bash_profile`)::

    export SECRET_KEY=djangosecretkey
    export DEBUG=1

Now create a database. If using postgres (strongly recommended; http://www.postgresql.org) create a database named ``sbox``, or check change the ``DB_URL`` env var from it's default, which is ``postgres://localhost/sbox``.



To deploy on heroku
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploying on Heroku_ is a good way of getting up an running quickly. To install you'll need the heroku command line tools and an account already setup.Then, from the base directory of the Signalbox project, run:
::

    heroku apps:create YOURAPPNAME
    heroku addons:add heroku-postgresql:dev
    heroku addons:add pgbackups
    heroku addons:add scheduler:standard

.. _Heroku: http://heroku.com

And also set the same env variables as above on heroku:
::
    heroku config:set SECRET_KEY=djangosecretkey





To deploy on your own server using Apache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See `sbox.wsgi` and `sbox_vhost.conf` to get things working with Apache.



Configuring the site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you have setup the django ``Site``  object correctly though the admin interface here ``/admin/sites/site/1/``. The url for the ``Site`` is used in multiple places, including when generating the callback links sent to participants.

Having already created a database, create the necessary tables by running:
::
    app/manage.py syncdb --all --noinput


..note:: To make things work on heroku, prefix with ``heroku run``

To load some configuration and an example study, run::

    app/manage.py loaddata sbox/signalbox/fixtures/initial_data_dontload.json

Note, if this file were called ``initial_data.json`` it would have been loaded on `syncdb`, but this isn't always desireable.


To create an administrator::

    app/manage.py createsuperuser


To create test users of each of the different roles for demonstration purposes::

    app/manage.py make_dummy_users





Email and SMS settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

API keys and passwords are stored in environment variables (see http://www.12factor.net/config).

It's recommended to use Amazon S3 (http://aws.amazon.com/s3/) to serve static assets (this is done automatically via django_compressor and the ``collectstatic`` command).::

    export AWS_STORAGE_BUCKET_NAME=bucket
    export AWS_ACCESS_KEY_ID=key
    export AWS_ACCESS_KEY_TOKEN=token


You can set your email relay with the follwing settings:::

    export EMAIL_HOST=YOUR_EMAIL_HOST
    export EMAIL_PORT=YOUR_EMAIL_PORT
    export EMAIL_HOST_USER=YOUR_EMAIL_HOST_USER
    export EMAIL_HOST_PASSWORD=YOUR_EMAIL_HOST_PASSWORD


..note:: The default is to require SSL and use port 465. We recommend using AWS SES (http://aws.amazon.com/ses/) or SendGrid because these services can ensure much higher rates of delivery and avoid mail being classified as spam.


A Twilio_ API key is required to send SMS messages or make telephone calls - these should be added to a TwilioAccount object, within the TwilioBox application.





Scheduled tasks and sending observations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We use django-kronos to create management tasks which run at regular intervals; see https://github.com/jgorset/django-kronos .


At the shell, you can send observations or reminders::

    app/manage.py runtask send
    app/manage.py runtask remind


For herkoku, open the scheduler interface and add the following commands:

::
    heroku addons:open scheduler

    app/manage.py runtask send
    app/manage.py runtask remind

..note:: These can be at any frequency you like, but bear in mind that if these jobs take a long time to run (with larger numbers of participants) then they may incur a (very) small cost from heroku, even using the free plan. You don't need to set up an additional worker dyno though.


On your own machine it's even easier, running `app/manage.py installtasks` will add the relevant entries to schedule sending of observations and reminders to the crontab.


..note:: You can also hit `/admin/signalbox/cron/` whenever you like, this will send all observations which are due.



Version control
~~~~~~~~~~~~~~~~~

Signalbox can use ``django_reversion`` to keep track of changes to Answer, Reply and Observation objects to provide an audit trail for a trial. It's not enabled by default, but to turn it on you can set an environment variable:

::
    export USE_VERSIONING=1




Browser compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The front-end (participant facing pages) should work in almost all browsers, including IE7.

The admin interface works best in a recent webkit browser (Safari or Chrome) but will largely function in IE7 (although the menus are slightly broken, they are usable). Everything will work properly in IE8 onwards.

.. note:: It's recommended to use Chrome-Frame if IE7 is the only available browser. See: `<https://developers.google.com/chrome/chrome-frame/>`_

.. warning:: Check everything works in your target browsers early in the trial setup. The health services and large firms have some weird and wonderful stuff deployed.





Running the tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The tests are not complete, but may nontheless be useful:
::
    app/manage.py test signalbox
    app/manage.py test ask






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

