import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from batterydataextractor.scrape import RSCWebScraper


class TestRSCScraper(unittest.TestCase):

    rsc_scraper = RSCWebScraper()

    def test_get_doi_rsc(self):
        dois = self.rsc_scraper.get_doi(query="battery materials", page=3)
        length = len(dois)

        self.assertEqual(length, 25)

    def test_els_scraper(self):
        # As Elsevier web-scraper requires API key, we have no tests here.
        # See examples/webscrape/elsevier.py for more details.
        pass

    def test_spr_scraper(self):
        # As Springer web-scraper requires API key, we have no tests here.
        # See examples/webscrape/spr.py for more details.
        pass


if __name__ == "__main__":
    unittest.main()
