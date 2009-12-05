import sys
import re
import cPickle as pickle
from django.utils import simplejson as json
from test_utils.testmaker import Testmaker
from test_utils.testmaker.processors.django_processor import Processor

if len(sys.argv) == 2:
    in_file = sys.argv[1]
else:
    raise Exception('Need file name')

f = open(in_file)

buffer = []

req_re = re.compile('---REQUEST_BREAK---')
res_re = re.compile('---RESPONSE_BREAK---')

processor = Processor('replay_processor')
tm = Testmaker()

tm.setup_logging('replay_file', '/dev/null')

serial_obj = pickle

class Request(dict):
    'Mocking a dict to allow attribute access'
    def __getattr__(self, name):
        return self[name]

for line in f.readlines():
    if req_re.search(line):
        #process request
        to_pickle = ''.join(buffer)
        request = Request(serial_obj.loads(to_pickle))
        processor.save_request(request)
        print request['path'], request['time']
        buffer = []
    elif res_re.search(line):
        #process response
        to_pickle = ''.join(buffer)
        response = Request(serial_obj.loads(to_pickle))
        processer.save_response(request, response)
        print response['status_code'], response['time']
        buffer = []
    else:
        buffer.append(line)
