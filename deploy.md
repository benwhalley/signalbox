---
layout: page
title: Deploy your own instance of signalbox
header: Deploy Signalbox now
group: navigation
permalink: /deploy/
---
{% include JB/setup %}


# Deploy Signalbox on Heroku for free!


Signalbox has been built for easy deployment on modern [software-as-a-service](http://en.wikipedia.org/wiki/Software_as_a_service) type platforms, including [Heroku](http://heroku.com). This means it's easy to deploy a copy of the software without developers or database experts on hand to manage it day-to-day.

It takes abotu 15 minutes to deploy a copy of Signalbox on Heroku, using their pushbutton deploy service. Before starting the setup you will need to:

- Register with [Twilio.com](https://www.twilio.com) and [get an access key and password](https://www.twilio.com/help/faq/twilio-basics/what-is-the-auth-token-and-how-can-it-be-reset)

As part of the setup you will

- Choose a name for your installation
- Set an administrator password and email address
- Register with Heroku and provide a credit card to validate your account (the defult setup is free however)


During the setup, Heroku will

- Create your own copy of the code
- Setup a database and configure daily backups
- Create a new administrative user and set the password you select
- Create a free account on [Mailgun](http://www.mailgun.com) for sending email
- Start a single web process running your site


Get started now:

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/puterleat/signalbox-example-project/tree/master)


### Final setup tasks

One task remains after the automatic setp: you must configure the scheduled tasks which periodically send emails, SMS messages and make telephone calls. Go to your [Heroku dashboard page](https://dashboard-next.heroku.com/apps/), select your new app and click on the button marked: ![](/assets/images/scheduledtasks.png)

Add two new tasks, entering the following commands:

<code>python app/manage.py send</code>

and

<code>python app/manage.py send</code>

You can set these to either hourly or every 10 minutes, depending on your needs.




### Custom domain names

You can add your own domain name to the app, but see



### Limitations

...






<a href="https://github.com/puterleat/signalbox"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/365986a132ccd6a44c23a9169022c0b5c890c387/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f7265645f6161303030302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png"></a>
