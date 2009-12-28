from django.test.simple import *
import os

def run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    worsk exactly as per normal test
    but only creates the test_db if it doesn't yet exist
    and does not destroy it when done
    tables are flushed and fixtures loaded between tests as per usual
    but if your schema has not changed then this saves significant amounts of time
    and speeds up the test cycle

    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - app.TestClass.test_method
        Run a single specific test method
     - app.TestClass
        Run all the test methods in a given class
     - app
        Search for doctests and unittests in the named application.

    When looking for tests, the test runner will look in the models and
    tests modules for the application.

    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.

    Returns the number of tests that failed.
    """
    setup_test_environment()

    settings.DEBUG = False
    suite = unittest.TestSuite()

    if test_labels:
        for label in test_labels:
            if '.' in label:
                suite.addTest(build_test(label))
            else:
                app = get_app(label)
                suite.addTest(build_suite(app))
    else:
        for app in get_apps():
            suite.addTest(build_suite(app))

    for test in extra_tests:
        suite.addTest(test)

    suite = reorder_suite(suite, (TestCase,))

    old_name = settings.DATABASE_NAME

    ###Everything up to here is from django.test.simple

    from django.db.backends import creation
    from django.db import connection, DatabaseError

    if settings.TEST_DATABASE_NAME:
        settings.DATABASE_NAME = settings.TEST_DATABASE_NAME
    else:
        settings.DATABASE_NAME = creation.TEST_DATABASE_PREFIX + settings.DATABASE_NAME
    connection.settings_dict["DATABASE_NAME"] = settings.DATABASE_NAME

    # does test db exist already ?
    try:
        if settings.DATABASE_ENGINE == 'sqlite3':
            if not os.path.exists(settings.DATABASE_NAME):
                raise DatabaseError
        cursor = connection.cursor()
    except DatabaseError, e:
        # db does not exist
        # juggling !  create_test_db switches the DATABASE_NAME to the TEST_DATABASE_NAME
        settings.DATABASE_NAME = old_name
        connection.settings_dict["DATABASE_NAME"] = old_name
        connection.creation.create_test_db(verbosity, autoclobber=True)
    else:
        connection.close()

    settings.DATABASE_SUPPORTS_TRANSACTIONS = connection.creation._rollback_works()

    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)

    #Since we don't call destory_test_db, we need to set the db name back.
    settings.DATABASE_NAME = old_name
    connection.settings_dict["DATABASE_NAME"] = old_name
    teardown_test_environment()

    return len(result.failures) + len(result.errors)
