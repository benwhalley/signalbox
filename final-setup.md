---
layout: page
title: Final setup of Signalbox on Heroku
header: Final setup
group: navigation
permalink: /deploy/final-setup.html
---
{% include JB/setup %}


> Congratulations---you're almost there...




One task remains after the automatic setp: you must configure the scheduled tasks which periodically send emails, SMS messages and make telephone calls. Go to your [Heroku dashboard page](https://dashboard-next.heroku.com/apps/), select your new app, and click on the button marked: ![](/assets/images/scheduledtasks.png)

Add two new tasks, entering the following commands to be run either hourly or every 10 minutes, depending on your needs:

<code>python app/manage.py send</code>

and

<code>python app/manage.py send</code>





### Limitations

Running under the free plan you are limited to a database of 9mb, and 300 emails sent per day. If you require more than you can scale up (and pay for) more resources on the Heroku dashboard.

You may also find that your application is slow to respond if there have been no visits for more than 10 minutes. See [here](https://blog.heroku.com/archives/2013/6/20/app_sleeping_on_heroku) for why this occurs and to official way to avoid it (it involves paying for at least one web dyno). [This page](http://stackoverflow.com/questions/5480337/easy-way-to-prevent-heroku-idling) also offers useful suggestions for those on a budget.




<a href="https://github.com/puterleat/signalbox"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/365986a132ccd6a44c23a9169022c0b5c890c387/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f7265645f6161303030302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png"></a>
