from base import Plugin
import re

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
