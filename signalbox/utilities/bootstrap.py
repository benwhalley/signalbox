"""Collects lots of things to setup on local machine and heroku, and tries to configure."""

from uuid import uuid1 
import envoy
import os
import shutil
import getpass


def example_project_dir():
    example_proj = os.path.join(os.path.realpath(os.path.dirname(__file__)), "../", "example_project")
    print example_proj
    


def setup_signalbox_heroku():
    from signalbox import configurable_settings
    from boto.s3.connection import S3Connection
    import heroku
    
    huser = raw_input("What is your heroku username (this might be an email address)? ")
    hpass = getpass.getpass("What is your heroku password? ")
    cloud = heroku.from_pass(huser, hpass )
    
    while 1:
        try:
            newname = raw_input("What name do you want to give you your new app on Heroku? ")
            app = cloud.apps.add(newname)
            print "Trying to link app to local repo..."
            # could check results of  git remote -v to see if already linked
            print envoy.run("git remote add heroku git@heroku.com:{}.git".format(newname)).std_out
            print "New app created on heroku and linked to the current working directory."
            open('.herokuappname', 'w').write(newname)
            break
        except Exception as e:
            print e

    app.addons.add('heroku-postgresql:dev')
    print "Added postgres database (free dev version) to app"
    
    print "Adding monthly database backups... If this is a serious study you should probably pay for daily or hourly backups."
    app.addons.add('pgbackups:auto-month')
    
    print "Adding scheduler..."
    app.addons.add('scheduler:standard')
    print "Scheduler service added, but you need to add the scheduled items manually (type 'heroku addons:open scheduler' when this has finished)"

    
    print "\nI'll now ask for some access details for Amazon, your email host and Twilio..."
    
    varstoget = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'EMAIL_HOST',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'TWILIO_ID',
        'TWILIO_TOKEN'
    ]
        
    getvar = lambda x: raw_input("Enter {} (or will set to {}): ".format(x, getattr(configurable_settings, x, "")))
    d = {i:getvar(i) for i in varstoget}
    
    
    # AMAZON STUFF
    
    while 1:
        try:
            s3conn = S3Connection(d['AWS_ACCESS_KEY_ID'], d['AWS_SECRET_ACCESS_KEY'])
            bucketname = raw_input("What (new and unique) name should I give to the new Amazon S3 bucket which will store static files for this site?")
            bucket = s3conn.create_bucket(bucketname)
            open('.bucket', 'w').write(bucketname)
            print "New bucket created."
            bucket.set_acl('public-read')
            print "Bucket set to public access, read only"
            break
        except Exception as e:
            print e 
    


    # CONFIGURING
    
    # add some extras
    d.update({
        'SECRET_KEY': uuid1().hex,
        'ALLOWED_HOSTS': ".herokuapp.com",
        'SECURE_SSL_REDIRECT': "1",
        'DEBUG': "1",
    })
    
    print "Updating config on heroku..."
    for k, v in d.items():
        app.config[k] = v
        

    print "Adding buildpack support for pandoc binaries..."
    app.config['BUILDPACK_URL']  = "https://github.com/ddollar/heroku-buildpack-multi.git"
    app.config['PATH'] = "bin:/usr/local/bin:/usr/bin:/bin"
    
    print "Config completed."
    print "Remember to turn DEBUG mode off before you launch."
    
    
    
    
    
    