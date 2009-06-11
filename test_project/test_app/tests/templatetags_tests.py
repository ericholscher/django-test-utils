from django.test.testcases import TestCase
from django.template import Context, Template
from django.contrib.auth.models import User
from test_utils.templatetags import TemplateParser

class Parsing(TestCase):
   """
   Tests to test the parsing API
   """

   def test_basic_parsing(self):
      t = TemplateParser('{% load test %}{% test parser_obj as as_var %}{{ as_var }}')
      t.parse()
      self.assertEquals(t.template_calls[0], '{% test parser_obj as as_var %}')
      self.assertEquals(t.loaded_classes[0], '{% load test %}')
