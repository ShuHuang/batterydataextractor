# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.rsc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Web-scraping papers from The Royal Society of Chemistry. Please get the permission from RSC before web-scraping.
author: Shu Huang (sh2009@cam.ac.uk)
"""
import re
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from .base import BaseWebScraper


class RSCWebScraper(BaseWebScraper):
    """

    """
    def __init__(self, url=None, max_wait_time=30, driver=None):
        """

        :param url:
        :param max_wait_time:
        :param driver:
        """
        self.url = url
        self.max_wait_time = max_wait_time
        self.driver = driver

    def get_doi(self, query, page):
        """

        :param page:
        :param query:
        :return:
        """
        if self.driver is None:
            driver = webdriver.Chrome()
        else:
            driver = self.driver

        if self.url is None:
            url = "http://pubs.rsc.org/en/results?searchtext="
            url = url + query
        else:
            url = self.url
        driver.get(url)
        wait = WebDriverWait(driver, self.max_wait_time)
        # To make sure we don't overload the server
        sleep(1)
        next_button = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[class^=paging__btn]")))[
            1]
        page_string = """document.querySelectorAll("a[class^=paging__btn]")[1].setAttribute("data-pageno", \""""\
                      + str(page) + """\")"""
        driver.execute_script(page_string)
        next_button.click()
        sleep(1)
        _ = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.capsule.capsule--article')))
        doi_lists = driver.find_elements(By.PARTIAL_LINK_TEXT, 'https://doi.org')
        dois = [doi.text for doi in doi_lists]
        return dois

    def download_doi(self, doi, file_location):
        """

        :param doi:
        :param file_location:
        :return:
        """
        doi = doi.split("org/")[-1]
        r = requests.get('http://doi.org/' + doi, headers={'User-Agent': 'Mozilla/5.0'})
        result = re.findall(r'https://pubs.rsc.org/en/content/articlehtml/.*?"', r.text)
        url = result[0][:-1]
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content

        result = self.get_rsc_abstract(web_content)
        exact_date = result['date'].split("/")
        doi = result['doi'].replace("/", "_")
        if len(exact_date) == 3:
            name = exact_date[0] + exact_date[1] + exact_date[2] + '_' + doi
        else:
            name = '00000000_' + doi

        with open(file_location + name + '.html', 'wb') as f:
            f.write(web_content)
        return

    @staticmethod
    def get_rsc_abstract(web_content):
        """

        :param web_content:
        :return:
        """
        soup = BeautifulSoup(web_content, features="html.parser")
        for i in soup.find_all("meta"):
            if i.has_attr("name"):
                if i['name'] == "DC.Identifier":
                    doi = i['content']
            if i.has_attr("name"):
                if i["name"] == "DC.Date":
                    date = i['content']
            if i.has_attr("name"):
                if i["name"] == "DC.title":
                    title = i['content']
            if i.has_attr("name"):
                if i["name"] == "citation_journal_title":
                    journal = i['content']
        abstract = soup.find_all("p", attrs={"class": "abstract"})[0].get_text()
        return {"title": title, "doi": doi, "date": date, "journal": journal, "abstract": abstract}
