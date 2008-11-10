
from django.template import Node, Template
from template_utils.nodes import ContextUpdatingNode
#from test_utils.templatetags.utils import context_for_object
from django import template 

register = template.loader()

def parse_ttag(token):
    bits = token.split_contents()
    tags = {}
    possible_tags = ['as', 'for', 'limit', 'exclude']
    for index, bit in enumerate(bits):
        if bit.strip() in possible_tags:
            tags[bit.strip()] = bits[index+1]
    return tags

def context_for_object(token, Node):
    """This is a function that returns a Node.
    It takes a string from a template tag in the format
    TagName for [object] as [context variable]
    """
    tags = parse_ttag(token)
    if len(tags) == 2:
        return Node(tags['for'], tags['as'])
    elif len(tags) == 1:
        return Node(tags['for'])
    else:
        #raise template.TemplateSyntaxError, "%s: Fail" % bits[]
        print "ERROR"
        
        
class FooNode():
    def __init__(self, por, _as='default'):
        print "Making Node: for:%s, as:%s" % (por, _as)

    
    
    @register.tag
    def map(parser, token):
        return context_for_object(token, FooNode, func)

    