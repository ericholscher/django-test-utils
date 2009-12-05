"""
This file is to test testmaker. It will run over the polls app and with the crawler and with test maker outputting things. Hopefully this will provide a sane way to test testmaker.
"""
from django.test.testcases import TestCase
from django.template import Context, Template
from django.contrib.auth.models import User
from test_utils.crawler.base import Crawler
from test_utils.testmaker import Testmaker
from django.conf import settings
import logging, os, sys, re

class CrawlerTests(TestCase):
    """
    Tests to test the Crawler API
    """
    urls = "test_project.polls.urls"
    fixtures = ['polls_testmaker.json']

    def test_basic_crawling(self):
        conf_urls = {}
        verbosity = 1
        c = Crawler('/', conf_urls=conf_urls, verbosity=verbosity)
        c.run()
        self.assertEqual(c.crawled, {'/': True, u'/1': True, u'/2': True})

    def test_relative_crawling(self):
        conf_urls = {}
        verbosity = 1
        c = Crawler('/1', conf_urls=conf_urls, verbosity=verbosity)
        c.run()
        self.assertEqual(c.crawled, {u'/1': True})



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

    def tearDown(self):
        #Teardown logging somehow?
        os.remove('test_file')
        os.remove('serialize_file')

    def test_basic_testmaker(self):
        self.tm.insert_middleware()
        self.client.get('/')
        logs = open('test_file')
        output = logs.read()
        self.assertTrue(output.find('[<Poll: What\'s up?>, <Poll: Test poll>]') != -1)

    def test_twill_processor(self):
        settings.TESTMAKER_PROCESSOR = 'twill'
        self.tm.insert_middleware()
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
