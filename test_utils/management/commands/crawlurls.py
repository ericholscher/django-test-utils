from collections import defaultdict
from optparse import make_option
import logging
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.admindocs.views import extract_views_from_urlpatterns

from test_utils.crawler.base import Crawler

class LogStatsHandler(logging.Handler):
    stats = defaultdict(int)

    def emit(self, record):
        self.stats[record.levelno] += 1

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-p', '--pdb', action='store_true', dest='pdb', default=False,
            help='Pass -p to drop into pdb on an error'),
        make_option('-f', '--fixture', action='store_true', dest='fixtures', default=False,
            help='Pass -f to create a fixture for the data.'),
        make_option('-s', '--safe', action='store_true', dest='html', default=False,
            help='Pass -s to check for html fragments in your pages.'),
        make_option('-t', '--time', action='store_true', dest='time', default=False,
            help='Pass -t to time your requests.'),
        make_option('-r', '--response', action='store_true', dest='response', default=False,
            help='Pass -r to store the response objects.'),
        #TODO
        make_option('-e', '--each', action='store', dest='each',
            type='int',
            help='TODO: Pass -e NUM to specify how many times each URLConf entry should be hit.'),
    )

    help = "Displays all of the url matching routes for the project."
    args = "[relative start url]"

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity', 1))

        if verbosity > 1:
            log_level = logging.DEBUG
        elif verbosity:
            log_level = logging.INFO
        else:
            log_level = logging.WARN

        crawl_logger = logging.getLogger('crawler')
        crawl_logger.setLevel(logging.DEBUG)
        crawl_logger.propagate = 0

        log_stats = LogStatsHandler()

        crawl_logger.addHandler(log_stats)

        console = logging.StreamHandler()
        console.setLevel(log_level)
        console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))

        crawl_logger.addHandler(console)

        if len(args) > 1:
            raise CommandError('Only one start url is currently supported.')
        else:
            start_url = args[0] if args else '/'

        if settings.ADMIN_FOR:
            settings_modules = [__import__(m, {}, {}, ['']) for m in settings.ADMIN_FOR]
        else:
            settings_modules = [settings]

        conf_urls = {}

        for settings_mod in settings_modules:
            try:
                urlconf = __import__(settings_mod.ROOT_URLCONF, {}, {}, [''])
            except Exception, e:
                logging.exception("Error occurred while trying to load %s: %s", settings_mod.ROOT_URLCONF, str(e))
                continue

            view_functions = extract_views_from_urlpatterns(urlconf.urlpatterns)
            for (func, regex) in view_functions:
                #Get function name and add it to the hash of URLConf urls
                func_name = hasattr(func, '__name__') and func.__name__ or repr(func)
                conf_urls[regex] = ['func.__module__', func_name]

            #Now we have all of our URLs to test

        c = Crawler(start_url, conf_urls=conf_urls, verbosity=verbosity)
        c.run()

        # We'll exit with a non-zero status if we had any errors
        max_log_level = max(log_stats.stats.keys())
        if max_log_level >= logging.ERROR:
            sys.exit(2)
        elif max_log_level >= logging.WARNING:
            sys.exit(1)
        else:
            sys.exit(0)
