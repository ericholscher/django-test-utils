from django import template

def parse_ttag(token, possible_tags=['as', 'for', 'limit', 'exclude']):
    """
    A function to parse a template tag.
    Pass in the token to parse, and a list of keywords to look for.

    It sets the name of the tag to 'tag_name' in the hash returned.

    Default list of keywords is::
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
        if bit.strip() in possible_tags:
            if len(bits) != index-1:
                tags[bit.strip()] = bits[index+1]
    return tags

def context_for_object(token, Node):
    """
    Example Usage

    This is a function that returns a Node.
    It takes a string from a template tag in the format
    TagName for [object] as [context variable]
    """
    tags = parse_ttag(token, ['for', 'as'])
    if len(tags) == 2:
        return Node(tags['for'], tags['as'])
    elif len(tags) == 1:
        return Node(tags['for'])
    else:
        #raise template.TemplateSyntaxError, "%s: Fail" % bits[]
        print "ERROR"
