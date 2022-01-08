# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.rsc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Web-scraping papers from The Royal Society of Chemistry. Please get the permission from RSC before web-scraping.
author: Shu Huang (sh2009@cam.ac.uk)
"""
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base import BaseWebScraper


class RSCWebScraper(BaseWebScraper):
    """

    """
    def __init__(self, query, page, max_wait_time=30, driver=None):
        """

        :param query:
        :param page:
        :param max_wait_time:
        :param driver:
        """
        self.query = query
        self.page = page
        self.max_wait_time = max_wait_time
        self.driver = driver

    def get_doi(self):
        """
        Get the DOIs from a single page in RSC
        :return:
        """
        if self.driver is None:
            driver = webdriver.Chrome()
        else:
            driver = self.driver

        url = "http://pubs.rsc.org/en/results?searchtext="
        url = url + self.query
        driver.get(url)
        wait = WebDriverWait(driver, self.max_wait_time)
        if self.page != 1:
            # To make sure we don't overload the server
            sleep(1)
            next_button = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[class^=paging__btn]")))[
                1]
            page_string = """document.querySelectorAll("a[class^=paging__btn]")[1].setAttribute("data-pageno", \""""\
                          + str(self.page) + """\")"""
            driver.execute_script(page_string)
            next_button.click()
            sleep(1)
            _ = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.capsule.capsule--article')))
            doi_lists = driver.find_elements(By.PARTIAL_LINK_TEXT, 'https://doi.org')
            dois = [doi.text for doi in doi_lists]
        return dois

    @staticmethod
    def download_doi(doi, file_location, file_name):
        """

        :param doi:
        :param file_location:
        :param file_name:
        :return:
        """
        web_content = requests.get(doi, headers={"User-Agent": "Mozilla/5.0"}).content
        with open(file_location + file_name + '.html', 'wb') as f:
            f.write(web_content)
        return
