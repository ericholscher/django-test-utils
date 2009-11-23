from optparse import make_option
import logging, os
from os import path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
from django.db import models

from test_utils.testmaker import Testmaker


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-a', '--app', action='store', dest='application',
            default=None, help='The name of the application (in the current \
                    directory) to output data to. (defaults to currect directory)'),
        make_option('-l', '--logdir', action='store', dest='logdirectory',
            default=os.getcwd(), help='Directory to send tests and fixtures to. \
            (defaults to currect directory)'),
        make_option('-x', '--loud', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
        make_option('-f', '--fixture', action='store_true', dest='fixture', default=False,
            help='Pass -f to not create a fixture for the data.'),
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
    )

    help = 'Runs the test server with the testmaker output enabled'
    args = '[server:port]'

    def handle(self, addrport='', *args, **options):

        app = options.get("application")
        verbosity = int(options.get('verbosity', 1))
        create_fixtures = options.get('fixture', False)
        logdir = options.get('logdirectory')
        fixture_format = options.get('format', 'xml')

        if app:
            app = models.get_app(app)

        if not app:
            #Don't serialize the whole DB :)
            create_fixtures = False

        testmaker = Testmaker(app, verbosity, create_fixtures, fixture_format, addrport)
        testmaker.prepare(insert_middleware=True)
        try:
            call_command('runserver', addrport=addrport, use_reloader=False)
        except SystemExit:
            if create_fixtures:
                testmaker.make_fixtures()
            else:
                raise
