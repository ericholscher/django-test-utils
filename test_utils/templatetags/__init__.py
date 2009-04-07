import re
import os
from django.conf import settings
from django.template.loaders.filesystem import load_template_source

DEFAULT_TAGS = ['autoescape' , 'block' , 'comment' , 'cycle' , 'debug' ,
'extends' , 'filter' , 'firstof' , 'for' , 'if' , 'else',
'ifchanged' , 'ifequal' , 'ifnotequal' , 'include' , 'load' , 'now' ,
'regroup' , 'spaceless' , 'ssi' , 'templatetag' , 'url' , 'widthratio' ,
'with' ]

tag_re = re.compile('({% (.*?) %})')

#output_ttag_tests(user_context, response.template[0])

### Template Tag Maker stuff

class TemplateParser(object):

    def __init__(self, template):
        self.template = template
        #Contains the strings of all loaded classes
        self.loaded_classes = []
        self.template_calls = []
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
                            #Parse structure here?
                            self.template_calls.append(full_command)


    def create_ttag_string(self, context_names, out_context, tag_string):
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


    def parse_ttag(self, token, required_tags=[], optional_tags=['as', 'for', 'limit', 'exclude']):
        """
        A function to parse a template tag.
        Pass in the token to parse, and a list of keywords to look for.

        It sets the name of the tag to 'tag_name' in the hash returned.

        Default list of optional keywords is::
            ['as', 'for', 'limit', 'exclude']

        >>> from django.template import Token, TOKEN_TEXT
        >>> from test_utils.templatetags.utils import parse_ttag
        >>> parse_ttag('super_cool_tag for my_object as bob', ['as'])
        {'tag_name': u'super_cool_tag', u'as': u'bob'}
        >>> parse_ttag('super_cool_tag for my_object as bob', ['as', 'for'])
        {'tag_name': u'super_cool_tag', u'as': u'bob', u'for': u'my_object'}

        """

        if isinstance(token, template.Token):
            bits = token.split_contents()
        else:
            bits = token.split(' ')
        tags = {'tag_name': bits.pop(0)}
        for index, bit in enumerate(bits):
            bit = bit.strip()
            if bit in required_tags or bit in optional_tags:
                if len(bits) != index-1:
                    tags[bit.strip()] = bits[index+1]
        return tags

if __name__ == "__main__":
    t = TemplateParser('admin_doc/view_index.html')
    t.parse()
    #from django.template import Context
    #t.output_tests(Context({'blah': 'BLAH'}))
    print '\n'.join(t.template_calls)
