import logging
import time

class Serializer(object):
    """A pluggable Serializer class"""

    name = "base"

    def __init__(self, name):
        """Constructor"""
        self.name = name
        self.ser = logging.getLogger('testserializer')
        #self.ser = logging.getLogger('testserializer-%s' % self.name)
        self.data = {}

    def process_request(self, request):
        request_dict = {
            'name': self.name,
            'time': time.time(),
            'path': request.path,

            'GET': request.GET,
            'POST': request.POST,
            'REQUEST': request.REQUEST,
            'method': request.method,
        }
        return request_dict

    def save_request(self, request):
        raise NotImplementedError

    def process_response(self, path, response):
        response_dict = {
            'name': self.name,
            'time': time.time(),
            'path': path,

            'context': response.context,
            'content': response.content,
            'status_code': response.status_code,
            'cookies': response.cookies,
            'headers': response._headers,
        }
        return response_dict

    def save_response(self, request, response):
        raise NotImplementedError
