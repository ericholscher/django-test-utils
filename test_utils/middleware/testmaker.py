from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment
import logging, re, os
from django.utils.encoding import force_unicode
from django import template
from django.template.defaultfilters import slugify
import time

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

tag_re = re.compile('({% (.*?) %})')

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
               user_context = get_user_context(r.context)
               output_user_context(user_context)
               try:
                  output_ttag_tests(user_context, r.template[0])
               except Exception, e:
                  #Another hack
                  print "Error! %s" % e

### Testmaker stuff

def log_request(request):
   log.info('\n\tdef test_%s_%s(self): ' % (slugify(request.path), slugify(time.time())))
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
      return ret.copy()
   else:
      return context_list

def output_user_context(context):
    for var in context:
        try:
            #Avoid memory addy's which will change.
            if not re.search("0x\w+", force_unicode(context[var])):
                log.info(u'\t\tself.assertEqual(unicode(r.context[-1]["%s"]), u"%s")' % (var, force_unicode(context[var])))
        except UnicodeDecodeError, e:
            #FIXME: This might blow up on odd encoding
            pass

### Template Tag Maker stuff

def output_ttag_tests(context, templ):
    #Loaded classes persist so this is hacked in.
    loaded_classes = []
    for dir in settings.TEMPLATE_DIRS:
        if os.path.exists(os.path.join(dir, templ.name)):
            template_file = open(os.path.join(dir,templ.name))
            temp_string = template_file.read()
            for line in temp_string.split('\n'):
                loaded_classes = parse_template_line(line, loaded_classes, context)

def parse_template_line(line, loaded_classes, context):
    #Context (that we care about) is just for a single tag
    out_context = {}
    context_names = []
    mat = tag_re.search(line)
    if mat:
        bits = mat.group(2).split() #tokens
        cmd = bits.pop(0).strip()
        if cmd == 'load':
            loaded_classes.append(mat.group(0))
        if cmd not in DEFAULT_TAGS and cmd not in 'end'.join(DEFAULT_TAGS):
            for bit_num, bit in enumerate(bits):
                try:
                    out_context[bit] = template.Variable(bit).resolve(context)
                except:
                    pass
                if bit == 'as':
                    context_names.append(bits[bit_num+1])
            create_ttag_string(context_names, out_context, loaded_classes, mat.group(0))
    return loaded_classes

def create_ttag_string(context_names, out_context, loaded_classes, tag_string):
    con_string = ""
    for var in context_names:
       con_string += "{{ %s }}" % var
    template_string = "%s%s%s" % (''.join(loaded_classes), tag_string, con_string)
    template_obj = template.Template(template_string)
    rendered_string = template_obj.render(template.Context(out_context))
    output_ttag(template_string, rendered_string, out_context)

def output_ttag(template_str, output_str, context):
    log.info('\t\ttmpl = template.Template(u"""%s""")' % template_str)
    context_str = "{"
    for con in context:
        try:
            tmpl_obj = context[con]
            context_str += "'%s': get_model('%s', '%s').objects.get(pk=%s)," % (con, tmpl_obj._meta.app_label, tmpl_obj._meta.module_name, tmpl_obj.pk )
        except:
            #sometimes there be integers here
            pass
    context_str += "}"

    log.info('\t\tcontext = template.Context(%s)' % context_str)
    log.info('\t\tself.assertEqual(tmpl.render(context), u"%s")' % output_str)
