import re
import os
from django.conf import settings
from django.template.loaders.filesystem import load_template_source
from django import template

DEFAULT_TAGS = ['autoescape' , 'block' , 'comment' , 'cycle' , 'debug' ,
'extends' , 'filter' , 'firstof' , 'for' , 'if' , 'else',
'ifchanged' , 'ifequal' , 'ifnotequal' , 'include' , 'load' , 'now' ,
'regroup' , 'spaceless' , 'ssi' , 'templatetag' , 'url' , 'widthratio' ,
'with' ]

tag_re = re.compile('({% (.*?) %})')

### Template Tag Maker stuff

class TemplateParser(object):

    def __init__(self, template, context=None):
        """
        Set the initial value of the template to be parsed

        Allows for the template passed to be a string of a template name
        or a string that represents a template.
        """
        self.template = template
        self.context = context
        #Contains the strings of all loaded classes
        self.loaded_classes = []
        self.template_calls = []
        self.tests = []
        #Accept both template names and template strings
        try:
            self.template_string, self.filepath = load_template_source(template)
        except:
            self.template_string = template
            self.filepath = None


    def parse(self):
        """
        Parse the template tag calls out of the template.
        This is ugly because of having more than 1 tag on a line.
        Thus we have to loop over the file, splitting on the regex, then
        looping over the split, matching for our regex again.
        Improvements welcome!
        """
        for line in self.template_string.split('\n'):
            split_line = tag_re.split(line)
            if len(split_line) > 1:
                for matched in split_line:
                    mat = tag_re.search(matched)
                    if mat:
                        full_command = mat.group(0)
                        cmd =  mat.group(2).split()[0].strip() #tokens
                        if cmd == 'load':
                            self.loaded_classes.append(full_command)
                        else:
                            if cmd not in DEFAULT_TAGS and cmd not in 'end'.join(DEFAULT_TAGS):
                                self.template_calls.append(full_command)


    def create_tests(self):
        """
        This yields a rendered template string to assert Equals against with
        the outputted template.
        """
        for tag_string in self.template_calls:
                #Try and find anything in the string that's in the context
                context_name = ''
                bits = tag_string.split()
                for bit_num, bit in enumerate(bits):
                    try:
                        out_context[bit] = template.Variable(bit).resolve(self.context)
                    except:
                        pass
                    if bit == 'as':
                        context_name = bits[bit_num+1]

                con_string = "{{ %s }}" % context_name
                template_string = "%s%s%s" % (''.join(self.loaded_classes), tag_string, con_string)
                import ipdb; ipdb.set_trace()
                try:
                    template_obj = template.Template(template_string)
                    rendered_string = template_obj.render(template.Context(out_context))
                except Exception, e:
                    print "EXCEPTION: %s" % e.message
                #self.tests.append(rendered_string)
                self.output_ttag(template_string, rendered_string, out_context)

    def output_ttag(self, template_str, output_str, context):
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

