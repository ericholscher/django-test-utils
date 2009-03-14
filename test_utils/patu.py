#!/usr/bin/env python

# TODO
# breadth-first searching, stopping after a given level
# ensure redirects are followed

import httplib2
import time
import random
import sys
from BeautifulSoup import BeautifulSoup
from multiprocessing import Process, Queue, current_process
from urlparse import urlsplit, urljoin, urlunsplit

from test_utils.crawler import Crawler
from test_utils.signals import post_request, pre_request, finish_run

class Patu(Crawler):
    """
    Multi-threaded backend for crawler.
    """
    def __init__(self, base_url, conf_urls={}, verbosity=1, **kwargs):
        super(Patu).__init__(base_url, conf_urls, verbosity, kwargs)
       
        self.seen_urls = {}
        self.queued_urls = {}
        self.processes = []


    def worker(self, input, output, constraint):
        """
        Function run by worker processes
        """
        try:
            h = httplib2.Http(timeout = 60)
            for url in iter(input.get, 'STOP'):
                pre_request.send(self, url=url, request_dict={})
                result = self.get_url(h, url, constraint)
                post_request.send(self, url=url, request_dict={})
                output.put(result)

        except KeyboardInterrupt:
            pass

    def get_url(self, h, url, constraint):
        """
        Function used to calculate result
        """
        links = []
        try:
            resp, content = h.request(url)
            soup = BeautifulSoup(content)
        except Exception, e:
            return (current_process().name, '', url, links)
        hrefs = [a['href'] for a in soup.findAll('a') if a.has_key('href')]
        for href in hrefs:
            absolute_url = urljoin(url, href.strip())
            parts = urlsplit(absolute_url)
            if parts.netloc in [constraint, ""] and parts.scheme in ["http", ""]:
                # Ignore the #foo at the end of the url
                no_fragment = parts[:4] + ("",)
                links.append(urlunsplit(no_fragment))
        return (current_process().name, resp.status, url, links)

    def run(self):

        spiders = getattr(self.kwargs, 'spiders', 1)
        verbose = getattr(self.kwargs, 'verbose', False)

        # Create queues
        task_queue = Queue()
        done_queue = Queue()

        # Submit first url
        try:
            url = unicode(self.base_url)
        except IndexError:
            print "Give the spiders a URL."
            sys.exit(1)
        if not url.startswith('http://'):
            url = "http://" + url
        host = urlsplit(url).netloc
        task_queue.put(url)
        queued_urls[url] = True

        try:

            # Start worker processes
            for i in range(spiders):
                p = Process(target=worker, args=(task_queue, done_queue, host))
                p.start()
                processes.append(p)

            while len(queued_urls) > 0:
                name, resp_status, url, links = done_queue.get()
                if resp_status == 200:
                    if options.verbose:
                        print "[%s] %s (from %s)" % (resp_status, url, queued_urls[url])
                        sys.stdout.flush()
                else:
                    print "[%s] %s (from %s)" % (resp_status, url, queued_urls[url])
                    sys.stdout.flush()
                del(queued_urls[url])
                seen_urls[url] = True
                for link in links:
                    if not seen_urls.has_key(link) and not queued_urls.has_key(link):
                        # remember what url referenced this link
                        queued_urls[link] = url
                        task_queue.put(link)
        except KeyboardInterrupt:
            pass
        finally:
            # Give the spiders a chance to exit cleanly
            for i in range(spiders):
                task_queue.put('STOP')
            for p in processes:
                # Forcefully close the spiders
                p.terminate()
                p.join()
