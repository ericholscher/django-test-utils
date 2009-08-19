from base import Plugin
from BeautifulSoup import BeautifulSoup

class Sanitize(Plugin):
    "Make sure your response is good"

    def post_request(self, sender, **kwargs):

        try:
            soup = BeautifulSoup(kwargs['response'].content)
            if soup.find(text='&lt;') or soup.find(text='&gt;'):
                print "%s has dirty html" % url
        except Exception, e:
            fo = open("temp.html", 'w')
            fo.write(kwargs['response'].content)
            fo.close()
            print 'bad html in file temp.html'
            raise e
                     
