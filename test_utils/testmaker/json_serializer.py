from base_serializer import Serializer
from django.utils import simplejson as json

class Serializer(Serializer):
    name = "json-serializer"

    def save_request(self, request):
        """Saves the Request to the serialization stream"""
        request_dict = self.process_request(request)
        request_dict['arg_dict'] = {}
        try:
            self.ser.info(json.dumps(request_dict))
            self.ser.info('---REQUEST_BREAK---')
        except (TypeError):
            pass

    def save_response(self, path, response):
        """Saves the Response-like objects information that might be tested"""
        response_dict = self.process_response(path, response)
        try:
            self.ser.info(json.dumps(response_dict))
            self.ser.info('---RESPONSE_BREAK---')
        except (TypeError):
            #Can't pickle wsgi.error objects
            pass
