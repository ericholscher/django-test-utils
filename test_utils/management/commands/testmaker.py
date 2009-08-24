from optparse import make_option
import logging, os
from os import path

from django.core.management.base import AppCommand, CommandError
from django.conf import settings
from django.core.management import call_command

from test_utils.testmaker import Testmaker

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

        testmaker = Testmaker(app, verbosity, create_fixtures, format, addrport)
        try:
            call_command('runserver', addrport=addrport, use_reloader=False)
        except SystemExit:
            if create_fixtures:
                testmaker.make_fixtures()
            else:
                raise
