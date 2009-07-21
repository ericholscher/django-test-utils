import re
import cPickle as pickle
from django.utils import simplejson as json
from test_utils.testmaker import setup_logging
from test_utils.testmaker.base_processor import Processer

in_file = '/Users/ericholscher/lib/artocrats/pieces/tests/pieces_testdata.pickle'
f = open(in_file)

buffer = []

req_re = re.compile('---REQUEST_BREAK---')
res_re = re.compile('---RESPONSE_BREAK---')

processor = Processer()

setup_logging('/Users/ericholscher/lib/artocrats/pieces/tests/redo.py', '/dev/null')

serial_obj = json

class Request(dict):
    'Mocking a dict to allow attribute access'
    def __getattr__(self, name):
        return self[name]

for line in f.readlines():
    if req_re.search(line):
        #process request
        to_pickle = ''.join(buffer)
        request = Request(serial_obj.loads(to_pickle))
        processor.log_request(request)
        print request['path'], request['time']
        buffer = []
    elif res_re.search(line):
        #process response
        to_pickle = ''.join(buffer)
        response = Request(serial_obj.loads(to_pickle))
        self.processer.process_response(request, response)
        print response['status_code'], response['time']
        buffer = []
    else:
        buffer.append(line)
