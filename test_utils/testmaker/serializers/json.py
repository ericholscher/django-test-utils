from base_serializer import Serializer
from django.utils import simplejson as json
from test_utils.testmaker.serializers import REQUEST_UNIQUE_STRING, RESPONSE_UNIQUE_STRING

class JsonSerializer(Serializer):

    name = "json"

    def save_request(self, request):
        """Saves the Request to the serialization stream"""
        request_dict = self.process_request(request)
        try:
            self.ser.info(json.dumps(request_dict))
            self.ser.info(REQUEST_UNIQUE_STRING)
        except (TypeError):
            #Can't serialize wsgi.error objects
            pass

    def save_response(self, request, response):
        """Saves the Response-like objects information that might be tested"""
        response_dict = self.process_response(request.path, response)
        try:
            self.ser.info(json.dumps(response_dict))
            self.ser.info(RESPONSE_UNIQUE_STRING)
        except (TypeError):
            #Can't serialize wsgi.error objects
            pass
