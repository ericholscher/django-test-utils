.. _test_runner:

Django Test Runner
==================

This is a tool for running Django app tests standalone

Introduction
------------

This script is fairly basic. Here is a quick example of how to use it::
    django_test_runner.py [path-to-app]

You must have Django on the PYTHONPATH prior to running this script. This
script basically will bootstrap a Django environment for you.

By default this script with use SQLite and an in-memory database. If you
are using Python 2.5 it will just work out of the box for you.
