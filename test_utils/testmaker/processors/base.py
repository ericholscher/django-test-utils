from django.template.defaultfilters import slugify as base_slugify
import logging
import re

def slugify(toslug):
    """
    Turn dashs into underscores to sanitize for filenames
    """
    return re.sub("-", "_", base_slugify(toslug))

class Processer(object):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger('testprocessor')
        #self.log = logging.getLogger('testprocessor-%s' % self.name)
        self.data = {}

    def shall_we_proceed(self, request):
        if 'media' in request.path or 'test_utils' in request.path:
            return False
        return True

    def process_request(self, request):
        raise NotImplementedError

    def save_request(self, request):
        raise NotImplementedError

    def process_response(self, request, response):
        raise NotImplementedError

    def save_response(self, request, response):
        raise NotImplementedError
