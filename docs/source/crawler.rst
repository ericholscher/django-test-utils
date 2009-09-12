.. _crawler:

Django Crawler
-----------------


Core features
~~~~~~~~~~~~~

The Crawler at the beginning loops through all of your URLConfs. It
then loads up all of the regular expressions from these URLConfs to
examine later. Once the crawler is done crawling your site, it will
tell you what URLConf entries are not being hit.


Usage
~~~~~

The crawler is implemented as a management command.

Step 1: Add `test_utils` to your `INSTALLED_APPS`

Step 2: The syntax for invoking the crawler looks like:

.. sourcecode:: python

     ./manage.py crawlurls [options] [relative_start_url]

Relative start URLs are assumed to be relative to the site root and should
look like 'some/path', 'home', or even '/'. The relative start URL will be
normalized with leading and trailing slashes if they are not provided. The
default relative start URL is '/'.

The crawler at the moment has 4 options implemented on it. It crawls your
site using the `Django Test Client
<http://docs.djangoproject.com/en/dev/topics/testing/#module-
django.test.client>`__ (so no network traffic is required!) This
allows the crawler to have intimate knowledge of your Django Code.
This allows it to have features that other crawlers can't have.


Options
~~~~~~~

-v --verbosity [0,1,2]
``````````````````````

Same as most django apps. Set it to 2 to get a lot of output. 1 is the
default, which will only output errors.


-t --time
`````````

The `-t` option, as the help says: Pass -t to time your requests. This
outputs the time it takes to run each request on your site. This
option also tells the crawler to output the top 10 URLs that took the
most time at the end of it's run. Here is an example output from
running it on my site with `-t -v 2`:

.. sourcecode:: python

    Getting /blog/2007/oct/17/umw-blog-ring/ ({}) from (/blog/2007/oct/17/umw-blog-ring/)
    Time Elapsed: 0.256254911423
    Getting /blog/2007/dec/20/logo-lovers/ ({}) from (/blog/2007/dec/20/logo-lovers/)
    Time Elapsed: 0.06906914711
    Getting /blog/2007/dec/18/getting-real/ ({}) from (/blog/2007/dec/18/getting-real/)
    Time Elapsed: 0.211296081543
    Getting /blog/ ({u'page': u'5'}) from (/blog/?page=4)
    Time Elapsed: 0.165636062622
    NOT MATCHED: account/email/
    NOT MATCHED: account/register/
    NOT MATCHED: admin/doc/bookmarklets/
    NOT MATCHED: admin/doc/tags/
    NOT MATCHED: admin/(.*)
    NOT MATCHED: admin/doc/views/
    NOT MATCHED: account/signin/complete/
    NOT MATCHED: account/password/
    NOT MATCHED: resume/
    /blog/2008/feb/9/another-neat-ad/ took 0.743204
    /blog/2007/dec/20/browser-tabs/#comments took 0.637164
    /blog/2008/nov/1/blog-post-day-keeps-doctor-away/ took 0.522269


-p --pdb
````````

This option allows you to drop into pdb on an error in your site. This
lets you look around the response, context, and other things to see
what happened to cause the error. I don't know how useful this will
be, but it seems like a neat feature to be able to have. I stole this
idea from nose tests.


-s --safe
`````````

This option alerts you when you have escaped HTML fragments in your
templates. This is useful for tracking down places where you aren't
applying safe correctly, and other HTML related failures. This isn't
implemented well, and might be buggy because I didn't have any broken
pages on my site to test on :)


-r --response
`````````````

This tells the crawler to store the response object for each site.
This used to be the default behavior, but doing this bloats up memory.
There isn't anything useful implemented on top of this feature, but
with this feature you get a dictionary of request URLs with responses
as their values. You can then go through and do whatever you want
(including examine the Templates rendered and Contexts.


Considerations
~~~~~~~~~~~~~~

At the moment, this crawler doesn't have a lot of end-user
functionality. However, you can go in and edit the script at the end
of the crawl to do almost anything. You are left with a dictionary of
URLs crawled, and the time it took, and response (if you use the `-r`
option).


Future improvements
~~~~~~~~~~~~~~~~~~~

There are a lot of future improvements that I have planned. I want to
enable the test client to login as a user, passed in from the command
line. This should be pretty simple, I just haven't implemented it yet.

Another thing that I want to do but isn't implemented is fixtures. I
want to be able to output a copy of the data returned from the crawler
run. This will allow for future runs of the crawler to diff against
previous runs, creating a kind of regression test.

A third thing I want to implement is an option to only evaluate each
URLConf entry X times. Where you could say "only hit
/blog/[year]/[month]/ 10 times". This goes on the assumption that you
are looking for errors in your views or templates, and you only need
to hit each URL a couple of times. This also shouldn't be hard, but
isn't implemented yet.

The big pony that I want to make is to use multiprocessing on the
crawler. The crawler doesn't hit a network, so it is CPU-bound.
However, running with CPUs with multiple cores, multiprocessing will
speed this up. A problem with it is that some of the timing stuff and
pdb things won't be as useful.

I would love to hear some people's feedback and thoughts on this. I
think that this could be made into a really awesome tool. At the
moment it works well for smaller sites, but it would be nice to be
able to test only certain URLs in an app. There are lots of neat
things I have planned, but I like following the release early, release
often mantra.
