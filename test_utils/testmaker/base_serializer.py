import cPickle as pickle
import logging
import time

ser = logging.getLogger('testserializer')

class Serializer(object):
    """A pluggable Serializer class"""

    name = "default"

    def __init__(self, name='default'):
        """Constructor"""
        self.data = {}
        self.name = name

    def save_request(self, request):
        """Saves the Request to the serialization stream"""
        request_dict = {
            'name': self.name,
            'time': time.time(),
            'path': request.path,

            'get': request.GET,
            'post': request.POST,
            'arg_dict': request.REQUEST,
        }
        ser.info(pickle.dumps(request_dict))
        ser.info('---REQUEST_BREAK---')

    def save_response(self, path, response):
        """Saves the Response-like objects information that might be tested"""
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
        try:
            ser.info(pickle.dumps(response_dict))
            ser.info('---RESPONSE_BREAK---')
        except (TypeError, pickle.PicklingError):
            #Can't pickle wsgi.error objects
            pass
