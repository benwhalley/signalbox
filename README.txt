Signalbox
============

SignalBox is a web application application designed to make it easy to run clinical and other studies. Signalbox makes it easy to recruit, take consent from, and follow-up large numbers of participants, using a customisable assessment schedule.

Read the docs: http://signalbox.readthedocs.org/en/latest/

Installation instructions are below.


OS Dependencies
----------------

On Ubuntu 12.04, you can install everything you need for a development machine like this::

	sudo apt-get install -y python-dev postgresql-server-dev-9.1 libjpeg-dev virtualenvwrapper libmagic-dev git mercurial zlib1g-dev libfreetype6 libfreetype6-dev
	export WORKON_HOME=~/Envs
	mkdir -p $WORKON_HOME
	source /usr/local/bin/virtualenvwrapper.sh


Local install
---------------

First make a database with postgres (for development, allow the local user permissions). Then use the included setup_signalbox command to make an example project (note, you can do all this manually, just look at the script and at settings.py in the example project)::
	
	createdb sbox
	setup_signalbox.sh
	
If everything works, open http://127.0.0.1:8000/admin  to view the admin site on your development machine.



Hosted installation
--------------------

To get it running on Heroku's free plan (which is ideal for normal sized studies), you first need to:

1. Sign up for an account with Heroky (https://devcenter.heroku.com/articles/quickstart) and install their command line tool.
 
2. Sign up with Amazon for an S3 storage account (this to host the static image files which cannot be kept on heroku). See http://aws.amazon.com. During the setup process you will need to enter your secret AWS ID and key, but this is not saved on the local machine.

3. Obtain the details  (host, username, password) for an SMTP email server you will use. Amazon's 'simple email service', SES, is good: http://aws.amazon.com/ses/

4. If you plan on using interactive telephone calls, sign up with Twilio and make a note of your secret ID and key: https://www.twilio.com.


Then inside the new directory created above run these commands::
	
	wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
	ssh-keygen
	heroku keys:add
	
	cd YOURPROJECT
	git init; git add -A
	git commit -a -m "initial commit"
	
	signalbox_heroku_quickstart
	
	git push heroku master
	heroku run app/manage.py syncdb; heroku run app/manage.py migrate	
	heroku apps:open	


Remember to add a scheduled task to send observations via the heroku control panel. The frequency is up to you - polling more often can cost more in dyno time if it overruns the free quota (but not much), but you'll want to add scheduled tasks for these scripts::

	app/manage.py runtask send
	app/manage.py runtask remind
	app/manage.py cleanup
	

	
Finally, when you are happy things are working, be sure to turn DEBUG mode off to avoid security problems:

	heroku config:set DEBUG=0
	
	


