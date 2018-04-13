---
layout: page
title: Deploy your own instance of signalbox
header: Deploy Signalbox now
group: navigation
permalink: /deploy/
---
{% include JB/setup %}


> You can deploy Signalbox on Heroku in about 15 minutes, for free.

Signalbox has been built for easy deployment on modern [software-as-a-service](http://en.wikipedia.org/wiki/Software_as_a_service) type platforms, including [Heroku](http://heroku.com). This means it's easy to deploy a copy of the software without developers or database experts on hand to manage it day-to-day.

It takes about 15 minutes to deploy a copy of Signalbox on Heroku, using their pushbutton deploy service. Before starting the setup you will need to:

As part of the setup you will:

- Register with Heroku and provide a credit card to validate your account (the default setup remains free, however)
- Set an administrator username, password and email address


Optionally, can also

- To use SMS messages and/or automated telephone calls, register with [Twilio.com](https://www.twilio.com) and [get an api access key and password](https://www.twilio.com/help/faq/twilio-basics/what-is-the-auth-token-and-how-can-it-be-reset)
- To display images on your study pages, register for Amazon's AWS service and [get an access key](http://aws.amazon.com/iam/).[^You can read an [introduction to Amazon S3 here](http://docs.aws.amazon.com/AmazonS3/latest/dev/Introduction.html).]

During the setup, Heroku will

- Create your own copy of the code
- Setup a [managed postgres database](https://www.heroku.com/postgres)
- Create a new administrative user and set the password you select
- Start a single [web process (dyno)](https://devcenter.heroku.com/articles/how-heroku-works) running your site


Get started now:

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/puterleat/signalbox-example-project/tree/master)


### Final setup tasks

Once the install is complete, there is one [final task to complete the process](/deploy/final-setup.html)










<a href="https://github.com/puterleat/signalbox"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/365986a132ccd6a44c23a9169022c0b5c890c387/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f7265645f6161303030302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png"></a>
