Signalbox
============


SignalBox is a web application application designed to make it easy to run clinical and other studies. Signalbox makes it easy to recruit, take consent from, and follow-up large numbers of participants, using a customisable assessment schedule.

Read the docs: http://signalbox.readthedocs.org/en/latest/


To install::
	
	mkvirtualenv signalbox_virtualenv
	pip install signalbox
	bootstrap_signalbox # asks for new project name
	newprojectname
	cd newprojectname
	pip install -r requirements.txt
	source local-environment-example.sh
	app/manage.py syncdb
	app/manage.py migrate
	app/manage.py runserver
	open 127.0.0.1:8000/admin

