import re
import cPickle as pickle

f = open('/Users/ericholscher/lib/test/playground/tests/playground_testdata.pickle')

buffer = []

req_re = re.compile('---REQUEST_BREAK---')
res_re = re.compile('---RESPONSE_BREAK---')

for line in f.readlines():
    if req_re.search(line):
        to_pickle = ''.join(buffer)
        obj = pickle.loads(to_pickle)
        print obj['path'], obj['time']
        buffer = []
    elif res_re.search(line):
        to_pickle = ''.join(buffer)
        obj = pickle.loads(to_pickle)
        print obj['status_code'], obj['time']
        buffer = []
    else:
        buffer.append(line)


