import sys
import re
import cPickle as pickle
from test_utils.testmaker import Testmaker
from test_utils.testmaker.processors.django_processor import Processor

class MockRequest(dict):
    'Mocking a dict to allow attribute access'
    def __getattr__(self, name):
        return self[name]

class Replay(object):

    def __init__(self, file_name, replay_file='replay_file'):
        self.file_name = file_name
        self.stream = open(self.file_name).readlines()
        self.tm = Testmaker()
        self.tm.setup_logging(replay_file, '/dev/null')
        self.processor = Processor('replay_processor')
        self.serial_obj = pickle

    def process(self):
        self.log = []

        buffer = []
        req_re = re.compile('---REQUEST_BREAK---')
        res_re = re.compile('---RESPONSE_BREAK---')

        for line in self.stream:
            if req_re.search(line):
                #process request
                to_pickle = ''.join(buffer)
                request = MockRequest(self.serial_obj.loads(to_pickle))
                self.processor.save_request(request)
                print request['path'], request['time']
                buffer = []
            elif res_re.search(line):
                #process response
                to_pickle = ''.join(buffer)
                response = MockRequest(self.serial_obj.loads(to_pickle))
                self.log.append(request, response)
                self.processer.save_response(request, response)
                print response['status_code'], response['time']
                buffer = []
            else:
                buffer.append(line)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        in_file = sys.argv[1]
    else:
        raise Exception('Need file name')

    replay = Replay(in_file)
    replay.process()