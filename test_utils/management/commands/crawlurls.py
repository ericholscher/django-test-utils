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
        make_option('-p', '--pdb', action='store', dest='USE_PDB', default=True,
            help='Pass -p to drop into pdb on an error'),
        make_option('-f', '--fixture', action='store_true', dest='FIXTURE', default=True,
            help='Pass -f to not create a fixture for the data.'),
    )

    args = '[server:port]'
    help = "Displays all of the url matching routes for the project."
    
    requires_model_validation = True
    
    def handle(self, *args, **options):
        
        if settings.ADMIN_FOR:
            settings_modules = [__import__(m, {}, {}, ['']) for m in settings.ADMIN_FOR]
        else:
            settings_modules = [settings]
        
        conf_urls = []
        for settings_mod in settings_modules:
            try:
                urlconf = __import__(settings_mod.ROOT_URLCONF, {}, {}, [''])
            except Exception, e:
                print ("Error occurred while trying to load %s: %s" % (settings_mod.ROOT_URLCONF, str(e)))
                continue
            view_functions = extract_views_from_urlpatterns(urlconf.urlpatterns)
            for (func, regex) in view_functions:
                conf_urls.append(regex)
                #views.append(simplify_regex(regex))
                #print func.__module__
                #func_name = hasattr(func, '__name__') and func.__name__ or repr(func)
                #print func_name
        
        #Now we have all of our URLs to test
        crawled_urls = run('/')
        import pdb; pdb.set_trace()
        output_nonmatching(conf_urls, crawled_urls.keys())
        
def dumb_get_url(c, url, request_dic={}):
    "Takes a url, and returns it with a list of links"
    parsed = urlparse.urlparse(url)
    returned_urls = []
    print "Getting %s (%s)" % (url, request_dic)
    resp = c.get(url, request_dic)
    soup = BeautifulSoup(resp.content)
    hrefs = [a['href'] for a in soup.findAll('a') if a.has_key('href')]
    for a in hrefs:
        parsed_href = urlparse.urlparse(a)
        if parsed_href.path.startswith('/') and not parsed_href.scheme:
            returned_urls.append(a)
        elif not parsed_href.scheme:
            #Relative path = previous path + new path
            returned_urls.append(parsed.path + a)
    return (url, resp, returned_urls)
        
def run(initial_path):
    setup_test_environment()
    c = Client(REMOTE_ADDR='127.0.0.1')
    not_crawled = [initial_path]
    already_crawled = {}
    
    while len(not_crawled) > 0:
        #Take top off not_crawled and evaluate it
        orig_url = url_target = not_crawled.pop(0)
        
        parsed = urlparse.urlparse(url_target)
        request_dic = dict(cgi.parse_qsl(parsed.query))
        if request_dic: #cut off the get params
            url_target = parsed.path
        #url now contains the path, request_dic contains get params
        
        url, resp, returned_urls = dumb_get_url(c, url_target, request_dic)
        already_crawled[orig_url] = (resp.context, resp.template)
        #Get the info on the page
        if not resp.status_code in (200,302, 301):
            print "FAIL: %s, Status Code: %s" % (url, resp.status_code)
        #Find its links
        for base_url in returned_urls:
            if base_url not in not_crawled and not already_crawled.has_key(base_url):
                not_crawled.append(base_url)
    
    return already_crawled

def output_nonmatching(conf_urls, loved_urls):
    "Run after the spider is done to show what URLConf entries got hit"
    for pattern in conf_urls:
        pattern = pattern.replace('^', '').replace('$', '').replace('//', '/')
        curr = re.compile(pattern)
        matched = False
        for url in loved_urls:
            if curr.search(url):
                matched = True
        if not matched:
            print "NOT MATCHED: %s" % pattern
