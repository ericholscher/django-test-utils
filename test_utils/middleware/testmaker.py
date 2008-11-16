from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment
import logging, re
from django.utils.encoding import force_unicode

log = logging.getLogger('testmaker')
print "Loaded Testmaker Middleware"

#Remove at your own peril
debug = getattr(settings, 'DEBUG', False)
if not debug:
   print "THIS CODE IS NOT MEANT FOR USE IN PRODUCTION"
   #return

class TestMakerMiddleware(object):
   def process_request(self, request):
      if 'test_client_true' not in request.REQUEST:
         log_request(request)
         if request.method.lower() == "get":
            setup_test_environment()
            c = Client()
            getdict = request.GET.copy()
            getdict['test_client_true'] = 'yes' #avoid recursion
            r = c.get(request.path, getdict)
            log_status(request.path, r)
            if r.context:
               con = get_user_context(r.context) 
               output_user_context(con)
            
def log_request(request):
   log.info('\n\tdef %s(self): ' % 'test_path')
   method = request.method.lower()
   request_str = "'%s', {" % request.path
   for dict in request.REQUEST.dicts:
      for arg in dict:
         request_str += "'%s': '%s', " % arg, request.REQUEST[arg]
   request_str += "}"
   log.info("\t\tr = c.%s(%s)" % (method, request_str))

def log_status(path, request):
   log.info("\t\tself.assertEqual(r.status_code, %s)" % request.status_code)

def get_user_context(context_list):
   #Ugly Hack. Needs to be a better way
   if isinstance(context_list, list):
      context_list = context_list[-1] #Last context rendered
      ret = context_list.dicts[-1]
      if ret == {}:
         ret = context_list.dicts[0]
      return ret
   else:
      return context_list
   
def output_user_context(context):
   for var in context:
      try: 
         if not re.search("0x\w+", force_unicode(context[var])): #Avoid memory addy's which will change.
            log.info(u'\t\tself.assertEqual(unicode(r.context[-1]["%s"]), u"%s")' % (var, unicode(context[var])))
      except Exception, e:
         #FIXME: This might blow up on odd encoding or 404s. 
         pass
   