from test_utils.signals import post_request, pre_request, finish_run
from django.test.client import Client
from BeautifulSoup import BeautifulSoup
import re, cgi, urlparse

class Crawler(object):
    """
    This is a class that represents a URL crawler in python
    """
    def __init__(self, base_url, conf_urls={}):
        self.base_url = base_url
        self.conf_urls = conf_urls
        self.VERBOSITY = 1
        self.not_crawled = [('START',self.base_url)]

        self.crawled = {}
        self.timed_urls = {}

        self.c = Client(REMOTE_ADDR='127.0.0.1')

    def _parse_urls(self, url, resp):
        parsed = urlparse.urlparse(url)
        soup = BeautifulSoup(resp.content)
        returned_urls = []
        hrefs = [a['href'] for a in soup.findAll('a') if a.has_key('href')]
        for a in hrefs:
            parsed_href = urlparse.urlparse(a)
            if parsed_href.path.startswith('/') and not parsed_href.scheme:
                returned_urls.append(a)
            elif not parsed_href.scheme:
                #Relative path = previous path + new path
                returned_urls.append(parsed.path + a)
        return returned_urls

    def get_url(self, from_url, url, request_dict={}):
        "Takes a url, and returns it with a list of links"

        if self.VERBOSITY > 0:
            print "Getting %s (%s) from (%s)" % (url, request_dict, from_url)

        pre_request.send(self, url=url, request_dict=request_dict)
        resp = self.c.get(url, request_dict)
        post_request.send(self, url=url, response=resp)

        returned_urls = self._parse_urls(url, resp)
        return (resp, returned_urls)

    def run(self):

        while len(self.not_crawled) > 0:
            #Take top off not_crawled and evaluate it
            from_url, to_url = self.not_crawled.pop(0)

            parsed = urlparse.urlparse(to_url)
            request_dict = dict(cgi.parse_qsl(parsed.query))
            url_path = parsed.path
            #url_path now contains the path, request_dict contains get params

            try:
                resp, returned_urls = self.get_url(from_url, url_path, request_dict)
            except Exception, e:
                print "Exception: %s (%s)" % (e, to_url)
                resp = ''
                returned_urls = []

            self.crawled[to_url] = True
            #Find its links
            for base_url in returned_urls:
                if base_url not in [to for fro,to in self.not_crawled] and not self.crawled.has_key(base_url):
                    self.not_crawled.append((to_url, base_url))

        finish_run.send(self)
        return self.crawled

class Plugin(object):
    """
    This is a class to represent a plugin to the Crawler.
    Subclass it and define a start or stop function to be called on requests.
    """
    request = None
    datastore = {}

    def __init__(self):
        pre_request.connect(self.start)
        post_request.connect(self.finish)
        finish_run.connect(self.print_report)

class Time(Plugin):
    """
    Follow the time it takes to run requests.
    """

    def __init__(self):
        #super(Time).__init__(self)
        pre_request.connect(self.start)
        post_request.connect(self.finish)

    def start(sender, **kwargs):
        import time
        url = kwargs['url']
        self.timed_urls[url] = time.time()

    def finish(sender, **kwargs):
        import time
        cur = time.time()
        url = kwargs['url']
        old_time = self.timed_urls[url]
        total_time = cur - old_time
        self.timed_urls = total_time

    def print_report(self):
        "Print the longest time it took for pages to load"
        alist = sorted(self.crawled_urls.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        for url, time in alist[:10]:
            print "%s took %f" % (url, time)

class URLConf(Plugin):
    """
    Plugin to check validity of URLConf.
    Run after the spider is done to show what URLConf entries got hit.
    """

    def print_report(self):
        for pattern in self.conf_urls.keys():
            pattern = pattern.replace('^', '').replace('$', '').replace('//', '/')
            curr = re.compile(pattern)
            matched = False
            for url in self.loved_urls:
                if curr.search(url):
                    matched = True
            if not matched:
                print "NOT MATCHED: %s" % pattern

class Graph(Plugin):
    "Make pretty graphs of your requests"


class Sanitize(Plugin):
    "Make sure your response is good"

    def finish(sender, **kwargs):
        if CHECK_HTML:
            if soup.find(text='&lt;') or soup.find(text='&gt;'):
                print "%s has dirty html" % url

class Pdb(Plugin):
    "Run pdb on fail"

    def finish(sender, **kwargs):
        if hasattr(resp, 'status_code'):
            if not resp.status_code in (200,302, 301):
                print "FAIL: %s, Status Code: %s" % (url, resp.status_code)
                if USE_PDB:
                    import pdb
                    pdb.set_trace()
