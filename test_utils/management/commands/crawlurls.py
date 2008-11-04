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


class Url():
    
    def __init__(self, url, from_url, **kwargs):
        self.from_url = from_url
        self.url = url
        
    def __unicode__(self):
        return "URL:%s (from %s)" % (self.url, self.from_url)
    
    def __str__(self):
        return "URL:%s (from %s)" % (self.url, self.from_url)
        

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
                if options.get('traceback', None):
                    import traceback
                    traceback.print_exc()
                print ("Error occurred while trying to load %s: %s" % (settings_mod.ROOT_URLCONF, str(e)))
                continue
            view_functions = extract_views_from_urlpatterns(urlconf.urlpatterns)
            for (func, regex) in view_functions:
                conf_urls.append(regex)
                #views.append(simplify_regex(regex))
                #print func.__module__
                #func_name = hasattr(func, '__name__') and func.__name__ or repr(func)
                #print func_name
        
        """ Now we have all of our URLs to test """
        
        
        def crawl_url(url_obj, already_crawled={}, test_logging_in=False):
            from_url, url = url_obj.from_url, url_obj.url
            if url not in already_crawled.keys():
                
                #Fetch URLs
                already_crawled[url] = url_obj
                print "Trying: %s (from %s)" % (url, from_url)
                parsed = urlparse.urlparse(url)
                dic = dict(cgi.parse_qsl(parsed.query))
                if dic: #cut off the get params
                    url = parsed.path
                resp = c.get(url, dic)
                if not resp.status_code in (200,302):
                    print "FAIL: %s, Status Code: %s" % (url, resp.status_code)
                    url_obj.status = resp.status_code
                    
                #Find more and recursively grab 'em
                for a in BeautifulSoup(resp.content).findAll('a'):
                    try:
                        parsed_href = urlparse.urlparse(a['href'])
                        if parsed_href.path.startswith('/') and not parsed_href.scheme:
                            crawl_url(Url(parsed_href.path, url), already_crawled)
                        elif not parsed_href.scheme:
                            crawl_url(Url(parsed.path + parsed_href.path), url, already_crawled)
                    except Exception, e:
                        #print "PARSE FAIL: A:%s Error:%s (from %s)" % (a, e, from_url)
                        pass
            if test_logging_in:
                USERNAME = 'test'
                PASSWORD = 'test'
                c.login(username=USERNAME, password=PASSWORD)
                print "AGAIN, LOGGED IN THIS TIME!"
                u = Url('/admin/', 'TRY_LOGGEDIN')
                crawl_url(u, already_crawled, False)
                
            return already_crawled
        
        
        def output_nonmatching(conf_urls, loved_urls):
            for pattern in conf_urls:
                pattern = pattern.replace('^', '').replace('$', '').replace('//', '/')
                curr = re.compile(pattern)
                matched = False
                for url in loved_urls:
                    if curr.search(url):
                        matched = True
                if not matched:
                    pass
                    #print "NOT MATCHED: %s" % pattern
        
        #USERNAME = 'etest'
        #PASSWORD = 'test'
        c = Client(REMOTE_ADDR='127.0.0.1')
        #c.login(username=USERNAME, password=PASSWORD)
        
        u = Url('/', 'CLI')
        loved_urls = crawl_url(u, {}, True)
        output_nonmatching(conf_urls, loved_urls)
