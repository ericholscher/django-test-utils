from base import Plugin
import csv
import logging

LOG = logging.getLogger("crawler")

try:
    from guppy import hpy
    ACTIVE = True
except:
    LOG.debug('Guppy plugin not found. If you want memory profiling `pip install guppy`')
    ACTIVE = False

class Heap(Plugin):
    """
    Calculate heap consumed before and after request
    """
    #Takes too much time to be on by default.
    #active = ACTIVE
    active = False

    def __init__(self, write_csv=False):
        super(Heap, self).__init__()
        self.heap_urls = self.data['heap_urls'] = {}
        self.hp = hpy()
        self.write_csv = write_csv
        if self.write_csv:
            self.csv_writer = csv.writer(open('heap.csv', 'w'))

    def pre_request(self, sender, **kwargs):
        url = kwargs['url']
        self.hp.setrelheap()

    def post_request(self, sender, **kwargs):
        url = kwargs['url']
        heap = self.hp.heap()
        self.heap_urls[url]=heap.size
        LOG.debug("%s: heap consumed: %s", url, self.heap_urls[url])
        if self.write_csv:
            self.csv_writer.writerow([url, heap.size])

    def finish_run(self, sender, **kwargs):
        "Print the most heap consumed by a view"
        alist = sorted(self.heap_urls.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        for url, mem in alist[:10]:
            LOG.info("%s: %f heap" % (url, mem))
