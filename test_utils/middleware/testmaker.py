from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment
from django.utils.encoding import force_unicode
from django import template
from django.template.defaultfilters import slugify as base_slugify
import logging, re, os, copy
import time
import cPickle as pickle
from cStringIO import StringIO
from test_utils.templatetags import DEFAULT_TAGS

log = logging.getLogger('testmaker')
ser = logging.getLogger('testserializer')

#Remove at your own peril.
#Thar be sharks in these waters.
debug = getattr(settings, 'DEBUG', False)
if not debug:
    print "THIS CODE IS NOT MEANT FOR USE IN PRODUCTION"
else:
    print "Loaded Testmaker Middleware"

def slugify(toslug):
    """
    Turn dashs into underscores to sanitize for filenames
    """
    return re.sub("-", "_", base_slugify(toslug))

class TestMakerMiddleware(object):
    def __init__(self):
        """
        Assign a Serializer and Processer

        Serializers will be pluggable and allow for custom recording.
        Processers will process the serializations into test formats.
        """
        self.serializer = Serializer()
        self.processer = Processer()

    def process_request(self, request):
        """
        Run the request through the testmaker middleware.
        This outputs the requests to the chosen Serializers.
        Possible running it through one or many Processors
        """
        #This is request.REQUEST to catch POST and GET
        if 'test_client_true' not in request.REQUEST:
            self.serializer.save_request(request)
            if request.method.lower() == "get":
                setup_test_environment()
                c = Client(REMOTE_ADDR='127.0.0.1')
                getdict = request.GET.copy()
                getdict['test_client_true'] = 'yes' #avoid recursion
                response = c.get(request.path, getdict)
                self.serializer.save_response(request.path, response)
                self.processer.process(request, response)


class Serializer(object):
    """A pluggable Serializer class"""

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
        ser.info(pickle.dumps(response_dict))
        ser.info('---RESPONSE_BREAK---')

class Processer(object):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self):
        """
        At some point this will hold where we choose what processor(s) to use
        """
        pass

    def process(self, request, response):
        """Turn the 2 requests into a unittest"""
        self.log_request(request)
        self.log_status(request.path, response)
        if response.context and response.status_code != 404:
            user_context = self.get_user_context(response.context)
            self.output_user_context(user_context)
            #This is where template tag outputting would go


    def log_request(self, request):
        #pickle.dump(request,stio_buffer,pickle.HIGHEST_PROTOCOL)
        #log.info(stio_buffer)

        log.info('\n\tdef test_%s_%s(self): ' % (slugify(request.path), slugify(time.time())))
        method = request.method.lower()
        request_str = "'%s', {" % request.path
        for dikt in request.REQUEST.dicts:
            for arg in dikt:
                request_str += "' %s ': ' %s ', " % (arg, request.REQUEST[arg])
        request_str += "}"
        log.info("\t\tr = c.%s(%s)" % (method, request_str))

    def log_status(self, path, request):
        #pickle.dump((path,request), stio_buffer,pickle.HIGHEST_PROTOCOL)
        #log.info(stio_buffer)

        log.info("\t\tself.assertEqual(r.status_code, %s)" % request.status_code)
        if request.status_code in [301, 302]:
            log.info("\t\tself.assertEqual(r['Location'], %s)" % request['Location'])

    def get_user_context(self, context_list):
        #Ugly Hack. Needs to be a better way
        if isinstance(context_list, list):
            context_list = context_list[-1] #Last context rendered
            ret = context_list.dicts[-1]
            if ret == {}:
                ret = context_list.dicts[0]
            try:
                return ret.copy()
            except Exception, e:
                return dict()

        else:
            return context_list

    def output_user_context(self,context):
        for var in context:
            try:
                #Avoid memory addy's which will change.
                if not re.search("0x\w+", force_unicode(context[var])):
                    log.info(u'''\t\tself.assertEqual(unicode(r.context[-1]["""%s"""]), u"""%s""")''' % (var, force_unicode(context[var])))
            except UnicodeDecodeError, e:
                pass

