from django.conf import settings
from django.test import Client
from django.test.utils import setup_test_environment
import logging, re, os, copy
from django.utils.encoding import force_unicode
from django import template
from django.template.defaultfilters import slugify as base_slugify
import time
import cPickle as pickle
from cStringIO import StringIO

log = logging.getLogger('testmaker')
ser = logging.getLogger('testserializer')

#Remove at your own peril.
#Thar be sharks in these waters.
debug = getattr(settings, 'DEBUG', False)
if not debug:
    print "THIS CODE IS NOT MEANT FOR USE IN PRODUCTION"
    #return
else:
    print "Loaded Testmaker Middleware"

DEFAULT_TAGS = ['autoescape' , 'block' , 'comment' , 'cycle' , 'debug' ,
'extends' , 'filter' , 'firstof' , 'for' , 'if' , 'else',
'ifchanged' , 'ifequal' , 'ifnotequal' , 'include' , 'load' , 'now' ,
'regroup' , 'spaceless' , 'ssi' , 'templatetag' , 'url' , 'widthratio' ,
'with' ]

tag_re = re.compile('({% (.*?) %})')

def slugify(toslug):
    """docstring for slugify"""
    return re.sub("-","_",base_slugify(toslug))

class TestMakerMiddleware(object):
    def __init__(self):
        """Assign a Serializer and Processer"""
        self.serializer = Serializer()
        self.processer = Processer()

    def process_request(self, request):
        if 'test_client_true' not in request.REQUEST:
            self.serializer.save_request(request)
            if request.method.lower() == "get":
                setup_test_environment()
                c = Client(REMOTE_ADDR='127.0.0.1')
                getdict = request.GET.copy()
                getdict['test_client_true'] = 'yes' #avoid recursion
                r = c.get(request.path, getdict)
                self.serializer.save_response(request.path, r)
                self.processer.process_req(request,(request.path,r))


class Serializer(object):
    """A pluggable Serializer class"""

    def __init__(self):
        """Constructor"""
        self.strio_buffer = StringIO()

    def save_request(self,request):
        """Saves the Request to the serialization stream"""
        pickle.dump(request,self.strio_buffer,pickle.HIGHEST_PROTOCOL)

    def save_response(self,path, request):
        """Saves the Response-like objects information that might be tested"""
        pickle.dump((path,request),self.strio_buffer,pickle.HIGHEST_PROTOCOL)

    def flush(self):
        """Flush buffered Serialization data to disk"""
        ser.info(self.strio_buffer)
        self.strio_buffer = StringIO()


class Processer(object):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self):
        """Constructor"""
        pass

    def process_req(self,request,rtuple):
        """Turn the 2 requests into a unittest"""
        self.log_request(request)
        response = rtuple[1]
        self.log_status(rtuple[0], response)
        if response.context and response.status_code != 404:
            user_context = get_user_context(response.context)
            output_user_context(user_context)
            try:
                output_ttag_tests(user_context, response.template[0])
            except Exception, e:
                #Another hack
                log.error("Error! %s" % e)


    def log_request(self,request):
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

    def log_status(self,path, request):
        #pickle.dump((path,request), stio_buffer,pickle.HIGHEST_PROTOCOL)
        #log.info(stio_buffer)

        log.info("\t\tself.assertEqual(r.status_code, %s)" % request.status_code)
        if request.status_code in [301, 302]:
            log.info("\t\tself.assertEqual(r['Location'], %s)" % request['Location'])

    def get_user_context(self,context_list):
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

    ### Template Tag Maker stuff

    def output_ttag_tests(self,context, templ):
        #Loaded classes persist so this is hacked in.
        loaded_classes = []
        for dir in settings.TEMPLATE_DIRS:
            if os.path.exists(os.path.join(dir, templ.name)):
                template_file = open(os.path.join(dir,templ.name))
                temp_string = template_file.read()
                for line in temp_string.split('\n'):
                    loaded_classes = parse_template_line(line, loaded_classes, context)

    def parse_template_line(self,line, loaded_classes, context):
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

    def create_ttag_string(self,context_names, out_context, loaded_classes, tag_string):
        con_string = ""
        for var in context_names:
            con_string += "{{ %s }}" % var
        template_string = "%s%s%s" % (''.join(loaded_classes), tag_string, con_string)
        template_obj = template.Template(template_string)
        rendered_string = template_obj.render(template.Context(out_context))
        output_ttag(template_string, rendered_string, out_context)

    def output_ttag(self,template_str, output_str, context):
        log.info('''\t\ttmpl = template.Template(u"""%s""")''' % template_str)
        context_str = "{"
        for con in context:
            try:
                tmpl_obj = context[con]
                context_str += "'%s': get_model('%s', '%s').objects.get(pk=%s)," % (con, tmpl_obj._meta.app_label, tmpl_obj._meta.module_name, tmpl_obj.pk )
            except:
                #sometimes there be integers here
                pass
        context_str += "}"

        log.info('''\t\tcontext = template.Context(%s)''' % context_str)
        log.info('''\t\tself.assertEqual(tmpl.render(context), u"""%s""")''' % output_str)
