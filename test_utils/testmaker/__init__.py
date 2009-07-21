import logging
import os
from os import path
from django.core import serializers
from test_utils.management.commands.relational_dumpdata import _relational_dumpdata
from django.template import Context, Template
from django.conf import settings

TESTMAKER_TEMPLATE = """
from django.test import TestCase
from django.test import Client
from django import template
from django.db.models import get_model
c = Client(REMOTE_ADDR="127.0.0.1")

class Testmaker(TestCase):
{% if create_fixtures %}
    fixtures = ["{{ fixture_file }}"]
{% else %}
    #fixtures = ["{{ app_name }}_testmaker"]
{% endif %}
"""

def make_fixtures(fixture_file, format, app):
    print "Creating fixture at " + fixture_file
    objects, collected = _relational_dumpdata(app, set())
    serial_file = open(fixture_file, 'a')
    try:
        serializers.serialize(format, objects, stream=serial_file, indent=4)
    except Exception, e:
        print ("Unable to serialize database: %s" % e)


def setup_logging(test_file='/tmp/testmaker_tests.py', serialize_file='/tmp/testmaker_serialized'):
    #supress other logging
    logging.basicConfig(level=logging.CRITICAL,
                        filename="/dev/null")

    log = logging.getLogger('testmaker')
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(test_file, 'a')
    handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(handler)

    log_s = logging.getLogger('testserializer')
    log_s.setLevel(logging.INFO)
    handler_s = logging.FileHandler(serialize_file, 'a')
    handler_s.setFormatter(logging.Formatter('%(message)s'))
    log_s.addHandler(handler_s)

    return (log, log_s)


def setup_testmaker(app, verbosity=1, create_fixtures=False, format='xml', addrport='', **kwargs):
    """
    Sets up the testmaker working directory and files/settings.
    """

    app_name = app.__name__.split('.')[-2]
    base_dir = path.dirname(app.__file__)
    #Assume we're writing new tests until proven otherwise
    new_tests = True

    #Figure out where to store data
    fixtures_dir = path.join(base_dir, 'fixtures')
    fixture_file = path.join(fixtures_dir, '%s_testmaker.%s' % (app_name, format))
    if create_fixtures:
        if not path.exists(fixtures_dir):
            os.mkdir(fixtures_dir)

    #Setup test and serializer files
    tests_dir = path.join(base_dir, 'tests')
    test_file = path.join(tests_dir, '%s_testmaker.py' % (app_name))
    serialize_file = path.join(tests_dir, '%s_testdata.pickle' % (app_name))

    if not path.exists(tests_dir):
        os.mkdir(tests_dir)
    if path.exists(test_file):
        new_tests = False

    if verbosity > 0:
        print "Handling app '%s'" % app_name
        print "Logging tests to %s" % test_file
        if create_fixtures:
            print "Logging fixtures to %s" % fixture_file

    log, log_s = setup_logging(test_file=test_file, serialize_file=serialize_file)

    if new_tests:
        t = Template(TESTMAKER_TEMPLATE)
        c = Context(locals())
        log.info(t.render(c))
    else:
        print "Appending to current log file"

    if verbosity > 0:
        print "Inserting TestMaker logging server..."
    settings.MIDDLEWARE_CLASSES += ('test_utils.testmaker.middleware.testmaker.TestMakerMiddleware',)

    return (fixture_file, test_file)
