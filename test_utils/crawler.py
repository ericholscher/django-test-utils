from test_utils import signals as test_signals
from django.test.client import Client
from BeautifulSoup import BeautifulSoup
import re, cgi, urlparse, time

def _parse_urls(url, resp):
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

class Crawler(object):
    """
    This is a class that represents a URL crawler in python
    """
    def __init__(self, base_url, conf_urls={}, verbosity=1):
        self.base_url = base_url
        self.conf_urls = conf_urls
        self.verbosity = verbosity

        #These two are what keep track of what to crawl and what has been.
        self.not_crawled = [('START',self.base_url)]
        self.crawled = {}

        self.c = Client(REMOTE_ADDR='127.0.0.1')

        self.plugins = []
        for plug in Plugin.__subclasses__():
            active = getattr(plug, 'active', True)
            if active:
                self.plugins.append(plug())



    def get_url(self, from_url, to_url):
        """
        Takes a url, and returns it with a list of links
        This uses the Django test client.
        """
        parsed = urlparse.urlparse(to_url)
        request_dict = dict(cgi.parse_qsl(parsed.query))
        url_path = parsed.path
        #url_path now contains the path, request_dict contains get params

        if self.verbosity > 0:
            print "Getting %s (%s) from (%s)" % (to_url, request_dict, from_url)

        test_signals.pre_request.send(self, url=to_url, request_dict=request_dict)
        resp = self.c.get(url_path, request_dict)
        test_signals.post_request.send(self, url=to_url, response=resp)
        returned_urls = _parse_urls(to_url, resp)
        test_signals.urls_parsed.send(self, fro=to_url, returned_urls=returned_urls)
        return (resp, returned_urls)

    def run(self):
        test_signals.start_run.send(self)
        while len(self.not_crawled) > 0:
            #Take top off not_crawled and evaluate it
            from_url, to_url = self.not_crawled.pop(0)
            #try:
            resp, returned_urls = self.get_url(from_url, to_url)
            """
            except Exception, e:
                print "Exception: %s (%s)" % (e, to_url)
                continue
            """
            self.crawled[to_url] = True
            #Find its links that haven't been crawled
            for base_url in returned_urls:
                if base_url not in [to for fro,to in self.not_crawled] and not self.crawled.has_key(base_url):
                    self.not_crawled.append((to_url, base_url))
        test_signals.finish_run.send(self)

class Plugin(object):
    """
    This is a class to represent a plugin to the Crawler.
    Subclass it and define a start or stop function to be called on requests.
    Define a print_report function if your plugin outputs at the end of the run.
    """
    global_data = {}

    def __init__(self):
        if hasattr(self, 'pre_request'):
            test_signals.pre_request.connect(self.pre_request)
        if hasattr(self, 'post_request'):
            test_signals.post_request.connect(self.post_request)
        if hasattr(self, 'start_run'):
            test_signals.start_run.connect(self.start_run)
        if hasattr(self, 'finish_run'):
            test_signals.finish_run.connect(self.finish_run)
        if hasattr(self, 'urls_parsed'):
            test_signals.urls_parsed.connect(self.urls_parsed)

        self.data = self.global_data[self.__class__.__name__] = {}

    """
    #These functions enable instance['test'] to save to instance.data
    def __setitem__(self, key, val):
        self.global_data[self.__class__.__name__][key] = val

    def __getitem__(self, key):
        return self.global_data[self.__class__.__name__][key]
    """

class Time(Plugin):
    """
    Follow the time it takes to run requests.
    """

    def __init__(self):
        super(Time, self).__init__()
        self.timed_urls = self.data['timed_urls'] = {}

    def pre_request(self, sender, **kwargs):
        url = kwargs['url']
        self.timed_urls[url] = time.time()

    def post_request(self, sender, **kwargs):
        cur = time.time()
        url = kwargs['url']
        old_time = self.timed_urls[url]
        total_time = cur - old_time
        self.timed_urls[url] = total_time
        print "Time taken: %s" % self.timed_urls[url]

    def finish_run(self, sender, **kwargs):
        "Print the longest time it took for pages to load"
        alist = sorted(self.timed_urls.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        for url, ttime in alist[:10]:
            print "%s took %f" % (url, ttime)

class URLConf(Plugin):
    """
    Plugin to check validity of URLConf.
    Run after the spider is done to show what URLConf entries got hit.
    """

    def finish_run(self, sender, **kwargs):
        for pattern in sender.conf_urls.keys():
            pattern = pattern.replace('^', '').replace('$', '').replace('//', '/')
            curr = re.compile(pattern)
            matched = False
            for url in sender.crawled:
                if curr.search(url):
                    matched = True
            if not matched:
                print "NOT MATCHED: %s" % pattern

class Graph(Plugin):
    "Make pretty graphs of your requests"

    def __init__(self):
        super(Graph, self).__init__()
        self.request_graph = self.data['request_graph'] = {}
        import pygraphviz
        self.graph = pygraphviz.AGraph(directed=True)

    def urls_parsed(self, sender, fro, returned_urls, **kwargs):
        from_node = self.graph.add_node(str(fro), shape='tripleoctagon')
        for url in returned_urls:
            if not self.graph.has_node(str(url)):
                node = self.graph.add_node(str(url))
            self.graph.add_edge(str(fro), str(url))

    def finish_run(self, sender, **kwargs):
        import ipdb; ipdb.set_trace()
        print "Making graph of your URLs, this may take a while"
        self.graph.layout(prog='dot')
        self.graph.draw('my_urls.svg')

class Sanitize(Plugin):
    "Make sure your response is good"

    def post_request(self, sender, **kwargs):
        soup = BeautifulSoup(kwargs['response'].content)
        if soup.find(text='&lt;') or soup.find(text='&gt;'):
            print "%s has dirty html" % url

class Pdb(Plugin):
    "Run pdb on fail"
    active = False

    def post_request(self, sender, **kwargs):
        url = kwargs['url']
        resp = kwargs['response']
        if hasattr(resp, 'status_code'):
            if not resp.status_code in (200,302, 301):
                print "FAIL: %s, Status Code: %s" % (url, resp.status_code)
                try:
                    import ipdb; ipdb.set_trace()
                except:
                    import pdb; pdb.set_trace()
