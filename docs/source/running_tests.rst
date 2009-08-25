.. _running_tests:


====================
How to run the tests
====================

Test utils does contain some tests. Not as many as I would like, but it has enough to check the basic functionality of the things it does.

Running the tests is pretty simple. You just need to go into the test_project, and then run::

    ./manage.py test --settings=settings

In order to run just the tests for test utils do::

    ./manage.py test test_app --settings=settings

It is also possible to just run a single class of the tests if you so wish::

    ./manage.py test test_app.TestMakerTests --settings=settings
