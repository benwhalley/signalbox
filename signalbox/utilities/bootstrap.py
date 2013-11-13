"""Collects lots of things to setup on local machine and heroku, and tries to configure."""

import json
from uuid import uuid1
import envoy
import os
import shutil
import getpass


def _get_settings():
    required = json.loads(open('CONFIG_REQUIRED.json').read())
    optional = json.loads(open('CONFIG_OPTIONAL.json').read())
    return required, optional


def example_project_dir():
    example_proj = os.path.join(os.path.realpath(os.path.dirname(__file__)), "../", "example_project")
    print example_proj


def signalbox_make_heroku_app():
    import heroku
    print "Creating a new app on Heroku and creating DB and Scheduler"
    required, optional = _get_settings()
    cloud = heroku.from_pass(required['HEROKU_USERNAME'], required['HEROKU_PASSWORD'])

    app = cloud.apps.add(required['HEROKU_APP_NAME'])
    print "Trying to link app to local repo..."
    # could check results of  git remote -v to see if already linked
    print envoy.run("git remote add heroku git@heroku.com:{}.git".format(required['HEROKU_APP_NAME'])).std_out
    print "New app created on heroku and linked to the current working directory."

    app.addons.add('heroku-postgresql:dev')
    print "Added postgres database (free dev version) to app"

    print "Adding monthly database backups... If this is a serious study you should probably pay for daily or hourly backups."
    app.addons.add('pgbackups:auto-month')

    print "Adding scheduler..."
    app.addons.add('scheduler:standard')
    print "Scheduler service added, but you need to add the scheduled items manually (type 'heroku addons:open scheduler' when this has finished)"

    _signalbox_configure_heroku(app)


def signalbox_make_s3_bucket():
    from boto.s3.connection import S3Connection
    print "Creating a new amazon bucket to save static files to"
    required, optional = _get_settings()
    s3conn = S3Connection(required['AWS_ACCESS_KEY_ID'], required['AWS_SECRET_ACCESS_KEY'])
    bucket = s3conn.create_bucket(required['AWS_STORAGE_BUCKET_NAME'])
    print "New bucket created."
    bucket.set_acl('public-read')


def _signalbox_configure_heroku(app):

    print "Setting environment variables on Heroku..."
    # CONFIGURING
    required, optional = _get_settings()

    # add some extras
    optional.update({
        'SECRET_KEY': uuid1().hex,
    })

    for k, v in required.items() + optional.items():
        app.config[k] = v

    print "Config completed."
    print "Remember to turn DEBUG mode off in production."






