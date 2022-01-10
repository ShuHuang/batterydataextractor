import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from batterydataextractor.scrape import RSCWebScraper


class TestRSCScraper(unittest.TestCase):

    rsc_scraper = RSCWebScraper()

    def test_get_doi(self):
        dois = self.rsc_scraper.get_doi(query="battery materials", page=3)
        length = len(dois)

        self.assertEqual(length, 25)
    #
    # def test_download_doi(self):
    #     doi = ""
    #     self.rsc_scraper.download_doi()


if __name__ == "__main__":
    unittest.main()
