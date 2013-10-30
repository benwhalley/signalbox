#!/bin/bash

mkvirtualenv sbox_virtualenv
# pip install signalbox
pip install -U -e git+https://github.com/bigfudge/signalbox.git@HEAD#egg=signalbox

echo "Name of the folder to create the new project in? [ENTER]:"
read newname
cp -r `signalbox_example_project_dir` $newname
echo  $newname
cd $newname

pip install -r requirements.txt
source local-environment-example.sh
app/manage.py syncdb
app/manage.py migrate
app/manage.py runserver
