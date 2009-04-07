import re

DEFAULT_TAGS = ['autoescape' , 'block' , 'comment' , 'cycle' , 'debug' ,
'extends' , 'filter' , 'firstof' , 'for' , 'if' , 'else',
'ifchanged' , 'ifequal' , 'ifnotequal' , 'include' , 'load' , 'now' ,
'regroup' , 'spaceless' , 'ssi' , 'templatetag' , 'url' , 'widthratio' ,
'with' ]

tag_re = re.compile('({% (.*?) %})')

"""
            try:
                output_ttag_tests(user_context, response.template[0])
            except Exception, e:
                #Another hack
                log.error("Error! %s" % e)
"""

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
