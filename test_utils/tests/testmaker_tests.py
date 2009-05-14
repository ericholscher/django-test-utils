"""
This file is to test testmaker. It will run over the polls app and with the crawler and with test maker outputting things. Hopefully this will provide a sane way to test testmaker.
"""
from django.test.testcases import TestCase
from django.template import Context, Template
from django.contrib.auth.models import User
from test_utils.crawler.base import Crawler
from test_utils.testmaker import setup_logging
from django.conf import settings
import logging, os, sys, re

class CrawlerTests(TestCase):
    """
    Tests to test the Crawler API
    """
    urls = "test_utils.tests.polls.urls"
    fixtures = ['/Users/ericholscher/lib/django-test-utils/test_utils/tests/polls/fixtures/polls_testmaker.json']

    def test_basic_crawling(self):
        conf_urls = {}
        verbosity = 1
        c = Crawler('/', conf_urls=conf_urls, verbosity=verbosity)
        c.run()
        self.assertEqual(c.crawled, {'/': True, u'/1': True, u'/2': True})


class TestMakerTests(TestCase):
    """
    Tests to test basic testmaker functionality.
    """
    urls = "test_utils.tests.polls.urls"
    fixtures = ['/Users/ericholscher/lib/django-test-utils/test_utils/tests/polls/fixtures/polls_testmaker.json']

    def setUp(self):
        setup_logging('test_file', 'serialize_file')

    def tearDown(self):
        #Teardown logging somehow?
        os.remove('test_file')
        os.remove('serialize_file')

    def test_basic_testmaker(self):
        settings.MIDDLEWARE_CLASSES += ('test_utils.testmaker.middleware.testmaker.TestMakerMiddleware',)
        self.client.get('/')
        logs = open('test_file')
        output = logs.read()
        self.assertTrue(output.find('[<Poll: What\'s up?>, <Poll: Test poll>]') != -1)
