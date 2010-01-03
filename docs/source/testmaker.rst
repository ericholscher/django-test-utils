.. _testmaker:

================
Django Testmaker
================

Source code
===========

This projects is now a part of `Django test utils </projects/django-
test-utils/>`__. The 0.2 release is available at `Pypi
<http://pypi.python.org/pypi/django-test-utils/0.2>`__


What is does
============

Django testmaker is an application that writes tests for your Django
views for you. You simply run a special development server, and it
records tests for your application into your project for you. Tests
will be in a Unit Test format, and it will create a separate test for
each view that you hit.


Usage
=====

Step 1: Add `test_utils` to your INSTALLED_APPS settings.

Step 2:

.. sourcecode:: python

     ./manage.py testmaker -a APP


This will start the development server with testmaker loaded in. APP
must be in installed apps, and it will use Django's mechanism for
finding it. It should look a little something like this:

.. sourcecode:: python

    eric@Odin:~/EH$ ./manage.py testmaker mine
    Handling app 'mine'
    Logging tests to /home/eric/Python/EH/mine/tests/mine_testmaker.py
    Appending to current log file
    Inserting TestMaker logging server...
    Validating models...
    0 errors found

    Django version 1.0.1 final, using settings 'EH.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.


Then, as you browse around your site it will create unit test files
for you, outputting the context variables and status code for each
view that you visit. The test file used is in
`APP/tests/APP_testmaker.py`. Once you have your tests written, you
simply have to add them into your `__init__.py`, and then run your
tests.

Step 3:

.. sourcecode:: python

    ./manage.py test -a APP

Testmaker Internal Basics
=========================

Testmaker now has a pluggable backend architecture. It includes the concept of a `Processor` and a `Serializer`. A `Serializer` is responsible for serializing your request and responses, so that they can be run again later. A `Processor` is response for taking these request and response objects and turning them into the actual Unit Tests.

API
---

Both processors and serializers follow the standard API direction that django serializers started. For example, to grab instances of both of them, use the following code::

    serializer = serializers.get_serializer('pickle')()
    processor = processors.get_processor('django')()

Serializers
-----------

Testmaker ships with 2 default serializers currently. They are the `json` and `pickle` backends.

Processors
----------

Testmaker currently ships with just one Processor, the `django` processor, which produces Django Testcase-style Unit Tests.

Extending Testmaker
===================

Adding a new backend for a Processor or Serializer is easy. They both provide a similar interface, which can be located in the base.py file in their respective directories.

The only two functions that are required for each backend are the ability to save a request and a response. They have obvious defitions, and you should look in their directory for examples.

save_request(self, request)
---------------------------

save_response(self, request, response)
--------------------------------------


Options
=======


-f --fixture
------------

If you pass the `-f` option to testmaker, it will create fixtures for
you. They will be saved in `APP/fixtures/APP_fixtures.FORMAT`. The
default format is XML because I was having problems with JSON.


--format
--------

Pass this in with a valid serialization format for Django. Options are
currently json, yaml, or xml.


--addrport
----------

This allows you to pass in the normal address and post options for
runserver.


Future improvements
===================

Force app filtering
-------------------

I plan on having an option that allows you to restrict the views to
the app that you passed in on the command line. This would inspect the
URLConf for the app, and only output tests matching those URLs. This
would allow you to fine tune your tests so that it is guaranteed to
only test views in the app.


Better test naming scheme
-------------------------

The current way of naming tests is a bit hackish, and could be
improved. It works for now, and keeps names unique, so it's achieving
that goal. Suggestions welcome for a better way to name things.
