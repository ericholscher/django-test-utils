from base import Plugin
import time
from guppy import hpy
import csv

class Heap(Plugin):
    """
    Calculate heap consumed before and after request
    """
    #active = False
    
    def __init__(self):
        super(Heap, self).__init__()
        self.heap_urls = self.data['heap_urls'] = {}        
        self.csv_writer = csv.writer(open('heap.csv', 'w'))
        self.hp = hpy()
        

    def pre_request(self, sender, **kwargs):
        url = kwargs['url']
        self.hp.setrelheap()

    def post_request(self, sender, **kwargs):        
        url = kwargs['url']
        heap = self.hp.heap()
        self.heap_urls[url]=heap.size        
        print "Heap consumed: %s" % self.heap_urls[url]
        self.csv_writer.writerow([url, heap.size])

    def finish_run(self, sender, **kwargs):
        "Print the most heap consumed by a view"
        alist = sorted(self.heap_urls.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        for url, mem in alist[:10]:
            print "%s took %f of heap" % (url, mem)



