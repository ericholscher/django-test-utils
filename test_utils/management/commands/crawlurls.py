from django.conf import settings
from django.core.management.base import BaseCommand
try:
    # 2008-05-30 admindocs found in newforms-admin brand
    from django.contrib.admindocs.views import extract_views_from_urlpatterns, simplify_regex
except ImportError:
    # fall back to trunk, pre-NFA merge
    from django.contrib.admin.views.doc import extract_views_from_urlpatterns, simplify_regex
        
from django.test.client import Client
from django.test.utils import setup_test_environment, teardown_test_environment
from BeautifulSoup import BeautifulSoup
import re, cgi, urlparse
from optparse import make_option
from django.test.utils import setup_test_environment

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

    #args = 'app'
    help = "Displays all of the url matching routes for the project."
    
    requires_model_validation = True
    
    def handle(self, *args, **options):
        
        USE_PDB = options.get('pdb', False)
        MAKE_FIXTURES = options.get('fixtures', False)
        CHECK_HTML = options.get('html', False)
        CHECK_TIME = options.get('time', False)
        STORE_RESPONSE = options.get('response', False)
        VERBOSITY = int(options.get('verbosity', 1))
        #EACH_URL = options.get('each', 100000)
        
        if settings.ADMIN_FOR:
            settings_modules = [__import__(m, {}, {}, ['']) for m in settings.ADMIN_FOR]
        else:
            settings_modules = [settings]
        
        conf_urls = {}
        for settings_mod in settings_modules:
            try:
                urlconf = __import__(settings_mod.ROOT_URLCONF, {}, {}, [''])
            except Exception, e:
                print ("Error occurred while trying to load %s: %s" % (settings_mod.ROOT_URLCONF, str(e)))
                continue
            view_functions = extract_views_from_urlpatterns(urlconf.urlpatterns)
            for (func, regex) in view_functions:
                #Get function name and add it to the hash of URLConf urls
                func_name = hasattr(func, '__name__') and func.__name__ or repr(func)
                conf_urls[regex] = ['func.__module__', func_name]
        
        def dumb_get_url(c, from_url, url, request_dic={}):
            "Takes a url, and returns it with a list of links"
            parsed = urlparse.urlparse(url)
            returned_urls = []
            if VERBOSITY > 1:
                print "Getting %s (%s) from (%s)" % (url, request_dic, from_url)
            time_to_run = ''
            if CHECK_TIME:
                resp, time_to_run = time_function(lambda: c.get(url, request_dic))
            else:
                resp = c.get(url, request_dic)
            soup = BeautifulSoup(resp.content)
            if CHECK_HTML:
                if soup.find(text='&lt;') or soup.find(text='&gt;'):
                    print "%s has dirty html" % url
            hrefs = [a['href'] for a in soup.findAll('a') if a.has_key('href')]
            for a in hrefs:
                parsed_href = urlparse.urlparse(a)
                if parsed_href.path.startswith('/') and not parsed_href.scheme:
                    returned_urls.append(a)
                elif not parsed_href.scheme:
                    #Relative path = previous path + new path
                    returned_urls.append(parsed.path + a)
            return (url, resp, time_to_run, returned_urls)
                
        def run(initial_path):
            setup_test_environment()
            c = Client(REMOTE_ADDR='127.0.0.1')
            not_crawled = [('CLI',initial_path)]
            already_crawled = {}
            
            while len(not_crawled) > 0:
                #Take top off not_crawled and evaluate it
                from_url, url_target = not_crawled.pop(0)
                orig_url = url_target
                parsed = urlparse.urlparse(url_target)
                request_dic = dict(cgi.parse_qsl(parsed.query))
                url_target = parsed.path
                #url now contains the path, request_dic contains get params
                
                try:
                    url, resp, time_to_run, returned_urls = dumb_get_url(c, from_url, url_target, request_dic)
                except Exception, e:
                    print "Exception: %s (%s)" % (e, url_target)
                    time_to_run = 0
                    resp = ''
                    returned_urls = []
                    url = 'ERR'
                if STORE_RESPONSE:
                    already_crawled[orig_url] = (resp, time_to_run)
                else:
                    already_crawled[orig_url] = time_to_run
                #Get the info on the page
                if hasattr(resp, 'status_code'):
                    if not resp.status_code in (200,302, 301):
                        print "FAIL: %s, Status Code: %s" % (url, resp.status_code)
                        if USE_PDB:
                            import pdb
                            pdb.set_trace()
                #Find its links
                for base_url in returned_urls:
                    if base_url not in [base for orig,base in not_crawled] and not already_crawled.has_key(base_url):
                        not_crawled.append((orig_url, base_url))
            
            return already_crawled
        
        def output_nonmatching(conf_urls, loved_urls):
            "Run after the spider is done to show what URLConf entries got hit"
            for pattern in conf_urls.keys():
                pattern = pattern.replace('^', '').replace('$', '').replace('//', '/')
                curr = re.compile(pattern)
                matched = False
                for url in loved_urls:
                    if curr.search(url):
                        matched = True
                if not matched:
                    print "NOT MATCHED: %s" % pattern
        
        def make_fixture(crawled_urls):
            "Serialize object to keep later"
            #Not implemented.
            return crawled_urls.keys()
        
        def longest_time(crawled_urls):
            "Print the longest time it took for pages to load"
            alist = sorted(crawled_urls.iteritems(), key=lambda (k,v): (v,k), reverse=True)
            for url, time in alist[:10]:
                print "%s took %f" % (url, time)
        
        def time_function(func, prnt=True):
            "Run the function passed in, printing the time elapsed"
            import time
            cur = time.time()
            ret = func()
            time_to_run = (time.time() - cur)
            if prnt and VERBOSITY > 1:
                print "Time Elapsed: %s " % time_to_run
            return (ret, time_to_run)
            
        
        
        #Now we have all of our URLs to test
        crawled_urls = run('/')
        output_nonmatching(conf_urls, crawled_urls.keys())
        if CHECK_TIME:
            longest_time(crawled_urls)
        if MAKE_FIXTURES:
            make_fixture(crawled_urls)
            
        