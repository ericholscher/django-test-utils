"""
This file is to test testmaker. It will run over the polls app and with the crawler and with test maker outputting things. Hopefully this will provide a sane way to test testmaker.
"""
from django.test.testcases import TestCase
from test_utils.crawler.base import Crawler

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
