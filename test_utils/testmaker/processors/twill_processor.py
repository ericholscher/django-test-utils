import time
import re
import base

from django.template import Template, Context
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

TEST_TEMPLATE = """go {{ path }}"""

STATUS_TEMPLATE = """code {{ status_code }}"""

#CONTEXT_TEMPLATE = '''find {{value}}'''
CONTEXT_TEMPLATE = ''

def safe_dict(dict):
    new_dic = {}
    for key,val in dict.iteritems():
        new_dic[key] = mark_safe(val)
    return new_dic

class Processor(base.Processer):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self, name='django'):
        super(Processor, self).__init__(name)

    def save_request(self, request):
        """ Actually write the request out to a file """
        if self.shall_we_proceed(request):
            self._log_request(request)

    def save_response(self, request, response):
        if self.shall_we_proceed(request):
            self._log_status(response)
            '''#TODO make this log sanely.
            if response.context and response.status_code != 404:
                context = self._get_context(response.context)
                self._log_context(context)
                #This is where template tag outputting would go
            '''

    def _log_request(self, request):
        method = request.method.lower()
        request_str = "'%s', {" % request.path
        for dikt in request.REQUEST.dicts:
            for arg in dikt:
                request_str += "'%s': '%s', " % (arg, request.REQUEST[arg])
        request_str += "}"

        template = Template(TEST_TEMPLATE)
        context = {
            'path': request.path,
            'time': base.slugify(time.time()),
            'method': method,
            'request_str': request_str,
        }
        context = Context(safe_dict(context))
        self.log.info(template.render(context))

    def _log_status(self, response):
        template = Template(STATUS_TEMPLATE)
        context = {
            'status_code': response.status_code,
        }
        if response.status_code in [301, 302]:
            context['location'] = response['Location']
        context = Context(safe_dict(context))
        self.log.info(template.render(context))

    def _get_context(self, context_list):
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

    def _log_context(self, context):
        template = Template(CONTEXT_TEMPLATE)
        for var in context:
            val = force_unicode(context[var])
            con = {
                'key': var,
                'value': val,
            }
            con = Context(safe_dict(con))
            try:
                #Avoid memory addy's which will change.
                if not re.search("0x\w+", val):
                    self.log.info(template.render(con))
            except UnicodeDecodeError, e:
                pass
