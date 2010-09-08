import logging
import re
import time

from django.template.defaultfilters import slugify as base_slugify
from django.template import Template, Context
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from test_utils.templatetags import TemplateParser

TEST_TEMPLATE = 'Override in Subclass'
STATUS_TEMPLATE = 'Override in Subclass'
CONTEXT_TEMPLATE = 'Override in Subclass'
#DISCARD_CONTEXT_KEYS = ('LANGUAGES',)
DISCARD_CONTEXT_KEYS = []

def safe_dict(dict):
    new_dic = {}
    for key,val in dict.iteritems():
        new_dic[key] = mark_safe(val)
    return new_dic

def slugify(toslug):
    """
    Turn dashs into underscores to sanitize for filenames
    """
    return re.sub("-", "_", base_slugify(toslug))

class Processer(object):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger('testprocessor')
        #self.log = logging.getLogger('testprocessor-%s' % self.name)
        self.data = {}

    def shall_we_proceed(self, request):
        if 'media' in request.path or 'test_utils' in request.path:
            return False
        return True

    def process_request(self, request):
        raise NotImplementedError

    def save_request(self, request):
        """ Actually write the request out to a file """
        if self.shall_we_proceed(request):
            self._log_request(request)

    def process_response(self, request, response):
        raise NotImplementedError

    def save_response(self, request, response):
        if self.shall_we_proceed(request):
            self._log_status(response)
            if response.context and response.status_code != 404:
                self._log_context(response.context)
                #This is where template tag outputting would go
                #Turned off until it gets betterer
                """
                parser = TemplateParser(response.template[0], context)
                parser.parse()
                parser.create_tests()
                """

    def _get_template(self, templatename):
        """Should be implemented in subclass"""
        raise NotImplementedError

    def _log_request(self, request):
        method = request.method.lower()
        request_str = "'%s', {" % request.path
        for dikt in request.REQUEST.dicts:
            for arg in dikt:
                request_str += "'%s': '%s', " % (arg, request.REQUEST[arg])
        request_str += "}"

        template = Template(self._get_template('test'))
        context = {
            'path': slugify(request.path),
            'time': slugify(time.time()),
            'method': method,
            'request_str': request_str,
        }
        context = Context(safe_dict(context))
        self.log.info(template.render(context))

    def _log_status(self, response):
        template = Template(self._get_template('status'))
        context = {
            'status_code': response.status_code,
        }
        if response.status_code in [301, 302]:
            context['location'] = response['Location']
        context = Context(safe_dict(context))
        self.log.info(template.render(context))

    def _get_context_keys(self, context):
        """Get the keys from the contexts(list) """
        keys = []
        for d in context.dicts:
            if isinstance(d, Context):
                keys += self._get_context_keys(d)
            keys += d.keys()
        return keys

    def _log_context(self, context):
        template = Template(self._get_template('context'))
        keys = []
        if isinstance(context, list):
            for c in context:
                keys += self._get_context_keys(c)
        else:
            keys += self._get_context_keys(context)
        keys = set(keys)

        # Skip some keys
        for discardkey in DISCARD_CONTEXT_KEYS:
            keys.discard(discardkey)

        for key in keys:
            val = force_unicode(context[key])
            con = {
                'key': key,
                'value': val,
            }
            con = Context(safe_dict(con))
            try:
                #Avoid memory addy's which will change.
                if not re.search("0x\w+", val):
                    self.log.info(template.render(con))
            except UnicodeDecodeError, e:
                pass
