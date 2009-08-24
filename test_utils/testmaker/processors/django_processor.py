import cPickle as pickle
import logging
import time
import re
from base import slugify

from django.template import Template, Context
from django.utils.encoding import force_unicode

TEST_TEMPLATE = """
    def test_{{path}}_{{time}}(self):
        r = c.{{method}}({{request_str}})

"""

STATUS_TEMPLATE = """
        self.assertEqual(r.status_code, {{status_code}})
        {% ifequal status_code 301 %}
            self.assertEqual(r['Location'], '{{location}}')
        {% endifequal %}
"""

CONTEXT_TEMPLATE = '''
        self.assertEqual(unicode(r.context[-1]['{{key}}']), u"""{{value}}""")
'''


class DjangoProcesser(object):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self, name='django'):
        super(DjangoProcesser, self).__init__(name)

    def save_request(self, request):
        """ Actually write the request out to a file """
        if self.shall_we_proceed(request):
            self._log_request(request)

    def save_response(self, request, response):
        if self.shall_we_proceed(request):
            self._log_status(request)
            if response.context and response.status_code != 404:
                context = self.get_context(response.context)
                self._log_context(context)
                #This is where template tag outputting would go

    def _log_request(self, request):
        method = request.method.lower()
        request_str = "'%s', {" % request.path
        for dikt in request.REQUEST.dicts:
            for arg in dikt:
                request_str += "'%s': '%s', " % (arg, request.REQUEST[arg])
        request_str += "}"

        template = Template(TEST_TEMPLATE)
        context = Context({
            'path': slugify(request.path),
            'time': slugify(time.time()),
            'method': method,
            'request_str': request_str,
        })
        self.log.info(template.render(context))

    def _log_status(self, request):
        template = Template(STATUS_TEMPLATE)
        context = Context({
            'status_code': request.status_code,
            'location': request['Location']
        })
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
            context = Context({
                'key': var,
                'value': val,
            })
            try:
                #Avoid memory addy's which will change.
                if not re.search("0x\w+", val):
                    self.log.info(template.render(context))
            except UnicodeDecodeError, e:
                pass
