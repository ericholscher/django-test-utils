import cPickle as pickle
import logging
import time

class Serializer(object):
    """A pluggable Serializer class"""

    name = "default"

    def __init__(self, name='default'):
        """Constructor"""
        self.name = name
        #self.ser = logging.getLogger(name)
        self.ser = logging.getLogger('testserializer')
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
        """Saves the Request to the serialization stream"""
        request_dict = self.process_request(request)
        self.ser.info(pickle.dumps(request_dict))
        self.ser.info('---REQUEST_BREAK---')

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


    def save_response(self, path, response):
        """Saves the Response-like objects information that might be tested"""
        response_dict = self.process_response(path, response)
        try:
            self.ser.info(pickle.dumps(response_dict))
            self.ser.info('---RESPONSE_BREAK---')
        except (TypeError, pickle.PicklingError):
            #Can't pickle wsgi.error objects
            pass
