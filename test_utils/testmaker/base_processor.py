import cPickle as pickle
import logging
import time
import re

from django.utils.encoding import force_unicode
from django.template.defaultfilters import slugify as base_slugify

log = logging.getLogger('testmaker')

def slugify(toslug):
    """
    Turn dashs into underscores to sanitize for filenames
    """
    return re.sub("-", "_", base_slugify(toslug))

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
