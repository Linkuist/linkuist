Collectr: collect and browse your links
=======================================

Collectr is a project that aims to collect and asynchronously process your links, to sum them up.

It's a django based project, and nvie/rq is used to process everything asynchronously.

For now it supports links from:

 * Twitter using the streaming API
 * IRC using a script in your IRSSI client
 * RSS
 * and a bookmarklet


Installation
------------

The project requires a lots of dependancies:

  * Django in version 1.5
  * Logbook in version 0.3
  * PyYAML in version 3.10
  * South in version 0.7.5
  * certifi in version 0.0.8
  * chardet in version 1.0.1
  * django-social-auth in version 0.6.9
  * httplib2 in version 0.7.4
  * lxml in version 2.3.4
  * nltk in version 2.0.1
  * oauth2 in version 1.5.211
  * oauthlib in version 0.1.3
  * redis in version 2.4.13
  * requests in version 0.13.1
  * rq in version 0.3.0
  * rsa in version 3.1.1
  * times in version 0.4
  * tweepy in version 1.9
  * webarticle2text
  * tastypie in version 0.9.12
  * praw in version 2.1.0

Configuration
-------------

As it is a django project, you need to edit your collectr/settings.py to add your database credentials.
You should probably add your own TWITTER_CONSUMER_KEY and your TWITTER_CONSUMER_SECRET informations.

Oh, and your own SECRET_KEY  too \o/


Processes
---------

This project requires a lot of asynchronous process to run. I usually have 6 process:

 * The uwsgi proceess
 * The ./manage.py twitter_collector
 * The ./manage.py reddit_collector
 * The rqworker rss_collector which periodically check for new rss
 * The rqworker link_indexing -v which unqueue link from redis
 * The rqscheduler which schedule new rss fetch


Notable projects
----------------

If you're looking for a RSS reader, take a look at _Feedhq: https://github.com/feedhq/feedhq/blob/master/README.rst
