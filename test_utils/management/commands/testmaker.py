from django.core.management.base import AppCommand, CommandError
from optparse import make_option
import sys, logging, os, re
from os import path
from django.db.models import get_model, get_models, get_app
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.core import serializers
from django.test.signals import template_rendered
from django.conf import settings
from django.core.management import call_command


class Command(AppCommand):
    option_list = AppCommand.option_list + (
        make_option('-f', '--fixture', action='store_true', dest='fixture',
            help='Pass -f to create a fixture for the data.'),
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--addrport', action='store', dest='addrport',
            type='string', help='port number or ipaddr:port to run the server on'),
    )

    help = 'Runs the test server with the testmaker output enabled for a specific app'
    args = '[app to test]'

    def handle_app(self, app, **options):

        verbosity = int(options.get('verbosity', 1))
        create_fixtures = options.get('fixture', False)
        format = options.get('format', 'xml')
        addrport = options.get('addrport', '')

        app_name = app.__name__.split('.')[-2]
        base_dir = path.dirname(app.__file__)
        #Assume we're writing new tests until proven otherwise
        new_tests = True

        #Figure out where to store data
        if create_fixtures:
            fixtures_dir = path.join(base_dir, 'fixtures')
            fixture_file = path.join(fixtures_dir, '%s_testmaker.%s' % (app_name, format))
            if not path.exists(fixtures_dir):
                os.mkdir(fixtures_dir)

        tests_dir = path.join(base_dir, 'tests')
        test_file = path.join(tests_dir, '%s_testmaker.py' % (app_name))
        if not path.exists(tests_dir):
            os.mkdir(tests_dir)
        if path.exists(test_file):
            new_tests = False

        if verbosity > 0:
            print "Handling app '%s'" % app_name
            print "Logging tests to %s" % test_file
            if create_fixtures:
                print "Logging fixtures to %s" % fixture_file

        #supress other logging
        logging.basicConfig(level=logging.CRITICAL,
                            filename="/dev/null")

        log = logging.getLogger('testmaker')
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(test_file, 'a')
        handler.setFormatter(logging.Formatter('%(message)s'))
        log.addHandler(handler)


        if new_tests:
            #TODO Use a template for this
            log.info('from django.test import TestCase')
            log.info('from django.test import Client')
            log.info('from django import template')
            log.info('from django.db.models import get_model')
            log.info('c = Client(REMOTE_ADDR="127.0.0.1")')
            log.info('class Testmaker(TestCase):')
            if create_fixtures:
                log.info('\tfixtures = ["%s"]' % fixture_file)
            else:
                log.info('\t#fixtures = ["%s"]' % app_name)
        else:
            print "Appending to current log file"

        if verbosity > 0:
            print "Inserting TestMaker logging server..."
        settings.MIDDLEWARE_CLASSES += ('test_utils.middleware.testmaker.TestMakerMiddleware',)

        try:
            call_command('runserver', addrport=addrport, use_reloader=False)
        except SystemExit:
            if create_fixtures:
                make_fixtures(fixture_file, format, app)
            sys.exit(0)


def make_fixtures(fixture_file, format, app):
    print "Creating fixture at " + fixture_file
    from test_utils.management.commands.relational_dumpdata import _relational_dumpdata
    objects, collected = _relational_dumpdata(app, set())
    serial_file = open(fixture_file, 'a')
    try:
        serializers.serialize(format, objects, stream=serial_file)
    except Exception, e:
        print ("Unable to serialize database: %s" % e)
