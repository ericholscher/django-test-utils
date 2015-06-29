import time
import logging
import csv
import os

from base import Plugin

LOG = logging.getLogger('crawler')

class Time(Plugin):
    """
    Follow the time it takes to run requests.
    """
    csv_writer = None

    def __init__(self):
        super(Time, self).__init__()
        self.timed_urls = self.data['timed_urls'] = {}
        
    def set_output_dir(self, output_dir=None):
        super(Time, self).set_output_dir(output_dir)

        if output_dir:
            self.csv_writer = csv.writer(open(os.path.join(output_dir, 'url_times.csv'), 'w'))

    def pre_request(self, sender, **kwargs):
        url = kwargs['url']
        self.timed_urls[url] = time.time()

    def post_request(self, sender, **kwargs):
        cur = time.time()
        url = kwargs['url']
        old_time = self.timed_urls[url]
        total_time = cur - old_time
        self.timed_urls[url] = total_time
        LOG.debug("Time taken: %s", self.timed_urls[url])
        
        if self.csv_writer:
            self.csv_writer.writerow((url, self.timed_urls[url]))

    def finish_run(self, sender, **kwargs):
        "Print the longest time it took for pages to load"
        alist = sorted(self.timed_urls.iteritems(), key=lambda (k,v): (v,k), reverse=True)
        for url, ttime in alist[:10]:
            LOG.info("%s took %f", url, ttime)

PLUGIN = Time