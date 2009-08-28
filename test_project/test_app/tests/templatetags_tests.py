import os
from django.test.testcases import TestCase
from django.template import Context, Template
from django.contrib.auth.models import User
from test_utils.templatetags import TemplateParser
from test_utils.testmaker import Testmaker

from django.contrib.auth.models import User

class Parsing(TestCase):
   """
   Tests to test the parsing API
   """

   def setUp(self):
      self.tm = Testmaker()
      self.tm.setup_logging('test_file', 'serialize_file')

   def tearDown(self):
      #Teardown logging somehow?
      os.remove('test_file')
      os.remove('serialize_file')

   def test_basic_parsing(self):
      user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
      user.save()
      c = Context({'object': user})
      t = TemplateParser('{% load comments %}{% get_comment_list for object as as_var %}{{ as_var }}', c)
      t.parse()
      self.assertEquals(t.template_calls[0], '{% get_comment_list for object as as_var %}')
      self.assertEquals(t.loaded_classes[0], '{% load comments %}')
      t.create_tests()
      logs = open('test_file')
      output = logs.read()
      self.assertTrue(output.find("{'object': get_model('auth', 'user')") != -1)
