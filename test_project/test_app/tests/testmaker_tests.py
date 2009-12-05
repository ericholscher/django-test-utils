"""
This file is to test testmaker. It will run over the polls app and with the crawler and with test maker outputting things. Hopefully this will provide a sane way to test testmaker.
"""
from django.test.testcases import TestCase
from test_utils.testmaker import Testmaker
from django.conf import settings
import os

class TestMakerTests(TestCase):
    """
    Tests to test basic testmaker functionality.
    """
    urls = "test_project.polls.urls"
    fixtures = ['polls_testmaker.json']

    def setUp(self):
        self.tm = Testmaker()
        self.tm.setup_logging('test_file', 'serialize_file')
        Testmaker.enabled = True
        self.tm.insert_middleware()

    def tearDown(self):
        #Teardown logging somehow?
        os.remove('test_file')
        os.remove('serialize_file')

    def test_basic_testmaker(self):
        self.client.get('/')
        logs = open('test_file')
        output = logs.read()
        self.assertTrue(output.find('[<Poll: What\'s up?>, <Poll: Test poll>]') != -1)

    def test_twill_processor(self):
        settings.TESTMAKER_PROCESSOR = 'twill'
        self.client.get('/')
        self.client.get('/1/')
        logs = open('test_file')
        output = logs.read()
        self.assertTrue(output.find('code 200') != -1)

    def test_not_inserting_multiple_times(self):
        """
        Test that the middleware will only be inserted once.
        """
        self.tm.insert_middleware()
        self.tm.insert_middleware()
        middleware = settings.MIDDLEWARE_CLASSES
        #A set of the middleware should be the same, meaning the item isn't in twice.
        self.assertEqual(sorted(list(middleware)), sorted(list(set(middleware))))
