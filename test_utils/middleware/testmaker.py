from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment
import logging, re, os
from django.utils.encoding import force_unicode
from django import template

log = logging.getLogger('testmaker')
print "Loaded Testmaker Middleware"

#Remove at your own peril
debug = getattr(settings, 'DEBUG', False)
if not debug:
   print "THIS CODE IS NOT MEANT FOR USE IN PRODUCTION"
   #return
   
DEFAULT_TAGS = ['autoescape' , 'block' , 'comment' , 'cycle' , 'debug' ,
'extends' , 'filter' , 'firstof' , 'for' , 'if' , 'else',
'ifchanged' , 'ifequal' , 'ifnotequal' , 'include' , 'load' , 'now' ,
'regroup' , 'spaceless' , 'ssi' , 'templatetag' , 'url' , 'widthratio' ,
'with' ]   

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
            if r.context and r.status_code != 404:
               con = get_user_context(r.context) 
               output_user_context(con)
               try:
                  output_ttag_tests(con, r.template[0])
               except Exception, e:
                  #Another hack
                  pass
            
def log_request(request):
   log.info('\n\tdef %s(self): ' % 'test_path')
   method = request.method.lower()
   request_str = "'%s', {" % request.path
   for dikt in request.REQUEST.dicts:
      for arg in dikt:
         request_str += "'%s': '%s'" % (arg, request.REQUEST[arg])
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
      except UnicodeDecodeError, e:
         #FIXME: This might blow up on odd encoding 
         pass

def output_ttag_tests(context, templ):
   tag_re = re.compile('({% (.*?) %})')
   for dir in settings.TEMPLATE_DIRS:
      if os.path.exists(os.path.join(dir, templ.name)):
         template_file = open(os.path.join(dir,templ.name))
         temp_string = template_file.read()
         loaded_classes = []
         out_context = {}
         context_names = []
         for line in temp_string.split('\n'):
            mat = tag_re.search(line)
            if mat:
               internal = mat.group(2) #tokens
               bits = internal.split()
               cmd = bits.pop(0).strip()
               if cmd == 'load':
                  loaded_classes.append(line)
               if cmd not in DEFAULT_TAGS and cmd not in 'end'.join(DEFAULT_TAGS):
                  for bit_num, bit in enumerate(bits):
                     try:
                        var1 = template.Variable(bit)
                        var2 = var1.resolve(context)
                        out_context[bit] = var2
                     except:
                        pass
                     if bit == 'as':
                        context_names.append(bits[bit_num+1])
                  con_string = ""
                  for var in context_names:
                     con_string += "{{ %s }}" % var
                  tmp_str = "%s%s%s" % (''.join(loaded_classes),line, con_string)
                  print tmp_str
                  tmp = template.Template(tmp_str)
                  rendered_string = tmp.render(template.Context(out_context))
                  output_ttag(tmp_str, rendered_string, out_context)

def output_ttag(template_str, output_str, context):
   log.info('\t\ttmpl = template.Template(%s)' % template_str)
   log.info('\t\tcontext = template.Context(%s)' % context)
   log.info('\t\tself.assertEqual(tmpl.render(context), "%s")' % output_str)
      