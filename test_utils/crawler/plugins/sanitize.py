from base import Plugin
from BeautifulSoup import BeautifulSoup

class Sanitize(Plugin):
    "Make sure your response is good"

    def post_request(self, sender, **kwargs):
        soup = BeautifulSoup(kwargs['response'].content)
        if soup.find(text='&lt;') or soup.find(text='&gt;'):
            print "%s has dirty html" % url
