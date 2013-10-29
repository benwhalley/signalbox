echo "What do you want to call your new project? [ENTER]:"
read newname
cp -r `signalbox_example_project_dir` $newname
cd $newname
pip install -r requirements.txt
source local-environment-example.sh
app/manage.py syncdb
app/manage.py migrate
app/manage.py runserver
