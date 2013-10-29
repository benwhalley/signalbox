bootstrap_signalbox
cd $SIGNALBOXNAME

chmod 755 app/manage.py
pip install -r requirements.txt

source local-environment-example.sh
app/manage.py syncdb
app/manage.py migrate
app/manage.py runserver
