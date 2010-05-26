
Persistent Database Test Runner
===============================

This code allows you to persist a database between test runs. It is really useful for running the same tests again and again, without incurring the cost of having to re-create the database each time.

.. note::

    Currently support for 1.2 is in a 1.2 compatible branch. This will be
    merged into trunk soon.


Management Command
------------------

To call this function, simply use the ``quicktest`` management command, instead of the ``test`` command. If you need to alter the schema for your tests, simply run the normal ``test`` command, and the normal destroy/create cycle will take place.


Test Runner
-----------

The functionality is actually implemented in a Test Runner located at ``test_utils.test_runners.keep_database``. If you want to use this as your default test runner, you can set the ``TEST_RUNNER`` setting to that value. This is basically all that the management command does, but in a temporary way.
