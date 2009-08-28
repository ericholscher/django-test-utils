from django.http import HttpResponse

import logging

from test_utils.testmaker.processors.base import slugify
from test_utils.testmaker import Testmaker

def set_logging(request, filename=None):
    if not filename:
        filename = request.REQUEST['filename']
    filename = slugify(filename)
    log_file = '/tmp/testmaker/tests/%s_tests_custom.py' % filename
    serialize_file = '/tmp/testmaker/tests/%s_serial_custm.py' % filename
    tm = Testmaker()
    tm.setup_logging(test_file=log_file, serialize_file=serialize_file)
    #tm.app_name = 'tmp'
    #tm.prepare_test_file()
    return HttpResponse('Setup logging %s' % tm.test_file)

def show_log(request):
    file = Testmaker.logfile()
    contents = open(file)
    return HttpResponse(contents.read(), content_type='text/plain')
    HttpResponse()
