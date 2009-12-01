import logging
import re

from base import Plugin

LOG = logging.getLogger("crawler")

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
                LOG.warning("This pattern was not matched by any crawled page: %s", pattern)
