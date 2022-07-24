# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.springer

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Springer web-scraper
"""
import six
import json
import requests
from bs4 import BeautifulSoup
from .base import BaseWebScraper


class SpringerMetaWebScraper(BaseWebScraper):
    """
    Springer web-scraper using the meta API.
    """
    def __init__(self, query, api_key):
        """
        :param query: query text (e.g. battery materials)
        :param api_key: API key from the Springer API Portal (https://dev.springernature.com/)
        """
        super().__init__()
        self.api_key = api_key
        self.query = query.replace(" ", '%20')

    def get_doi(self, year=2022, start=0, max_return=100):
        """
        Get a list of dois of the query, year, and start index
        :param year: the year of published papers
        :param start: the start index of the returned papers
        :param max_return: the maximum number of returned papers (max: 100)
        :return: a list of dois of the query and year
        """
        url = "http://api.springernature.com/meta/v2/json?&q={}%20type:Journal%20year:{}&s={}&p={}&api_key={}".format(
            self.query, year, start, max_return, self.api_key)
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content
        content = json.loads(web_content.decode('utf-8'))
        dois = [content['records'][i]['doi'] for i in range(max_return)]
        return dois

    def get_xml(self, doi):
        """
        Get the xml link of the doi
        :param doi: the doi of a paper
        :return: the xml url
        """
        url = "https://api.springernature.com/meta/v2/pam?q=doi:{}&p=2&api_key={}".format(doi, self.api_key)
        return url

    def download_doi(self, doi, file_location):
        """
        Download the Springer xml paper
        :param doi: the doi of a paper
        :param file_location: saving location
        :return:
        """
        url = self.get_xml(doi)
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content
        result = self.get_spr_abstract(web_content)
        doi = result['doi'].replace("/", "_")
        date = result['date']
        name = date + "_" + doi
        with open(file_location + name + '.xml', 'wb') as f:
            f.write(web_content)
            f.close()
        return

    @staticmethod
    def get_spr_abstract(spr_document):
        """
        Get the metadata and abstract from a Springer xml file
        :param spr_document: Springer xml content
        :return: a dictionary of metadata and abstract
        """
        soup = BeautifulSoup(spr_document, features="html.parser")
        abstract = ''
        for i in soup.find_all("p"):
            if i.parent.name == "abstract":
                abstract = i.text.split("\documentclass")[0]
                abstract = abstract.replace("\n", "")
                abstract = abstract.replace("\t", "")
        date = soup.find_all("prism:publicationdate")[0].get_text()
        doi = soup.find_all("prism:doi")[0].get_text()
        journal = soup.find_all("prism:publicationname")[0].get_text()
        title = soup.find_all("dc:title")[0].get_text()
        return {"title": title, "doi": doi, "date": date, "journal": journal, "abstract": abstract}


class SpringerTDMWebScraper(BaseWebScraper):
    """
    Springer web-scraper using the TDM full-text API.
    """
    def __init__(self, query, api_key):
        """
        :param query: query text (e.g. battery materials)
        :param api_key: API key from the Springer API Portal (https://dev.springernature.com/)
        """
        super().__init__()
        self.api_key = api_key
        self.query = query.replace(" ", '%20')

    def get_doi(self, date_from="2020-06-01", date_to="2021-01-10", start=0, max_return=100):
        """
        Get a list of dois of the query, year, and start index
        :param date_from: the starting date of papers to be downloaded
        :param date_to: the end date of papers to be downloaded
        :param start: the start index of the returned papers
        :param max_return: the maximum number of returned papers (max: 100)
        :return: a list of dois of the query and year
        """
        url = "https://articles-api.springer.com/xmldata/jats?q={}%20onlinedatefrom:{}%20onlinedateto:{}&s={}" \
              "&p={}&api_key={}".format(self.query, date_from, date_to, start, max_return, self.api_key)
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content
        soup = BeautifulSoup(web_content, features="html.parser")
        doi = soup.find_all("article-id", attrs={"pub-id-type": "doi"})
        dois = [i.text for i in doi]
        return dois

    def get_xml(self, doi):
        """
        Get the xml link of the doi
        :param doi: the doi of a paper
        :return: the xml url
        """
        url = "https://articles-api.springer.com/xmldata/jats?q=doi:{}&api_key={}".format(doi, self.api_key)
        return url

    def download_doi(self, doi, file_location):
        """
        Download the Springer xml paper
        :param doi: the doi of a paper
        :param file_location: saving location
        :return:
        """
        url = self.get_xml(doi)
        web_content = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).content
        result = self.get_spr_abstract(web_content)
        doi = result['doi'].replace("/", "_")
        date = result['date']
        name = date + "_" + doi
        with open(file_location + name + '.xml', 'wb') as f:
            f.write(web_content)
            f.close()
        return

    @staticmethod
    def get_spr_abstract(spr_document):
        """
        Get the metadata and abstract from a Springer xml jats file
        :param spr_document: Springer xml jats content
        :return: a dictionary of metadata and abstract
        """
        soup = BeautifulSoup(spr_document, features="html.parser")
        abstract = ''
        for i in soup.find_all("p"):
            if i.parent.name == "abstract":
                abstract = i.text.split("\documentclass")[0]
                abstract = abstract.replace("\n", "")
                abstract = abstract.replace("\t", "")
        doi = soup.find_all("article-id", attrs={"pub-id-type": "doi"})[0].get_text()
        date = soup.find_all("pub-date", attrs={"date-type": "pub"})[0]
        year = date.find('year').get_text()
        try:
            month = date.find('month').get_text()
            if len(month) == 1:
                month = '0' + month
        except AttributeError:
            month = '01'
        try:
            day = date.find('day').get_text()
            if len(day) == 1:
                day = '0' + day
        except AttributeError:
            day = '01'
        date = year + month + day
        journal = soup.find_all("journal-title")[0].get_text()
        title = soup.find_all("article-title")[0].get_text()
        return {"title": title, "doi": doi, "date": date, "journal": journal, "abstract": abstract}


def spr_clean_abstract(document):
    """ Remove <title> in <abstract>"""
    # selects all tags and checks if the text or tail are spaces
    for el in document.xpath('.//abstract'):
        next_els = el.getchildren()
        for next_el in next_els:
            if next_el.tag == 'title':
                parent = next_el.getparent()
                if parent is None:
                    continue
                if next_el.tail:
                    previous = next_el.getprevious()
                    if previous is None:
                        parent.text = (parent.text or '') + next_el.tail
                    else:
                        previous.tail = (previous.tail or '') + next_el.tail
                parent.remove(next_el)
    return document


def spr_clean_ref(document):
    """Remove <article-title> in <ref>"""
    for el in document.xpath('.//ref'):
        next_els = el.getchildren()
        for next_el in next_els:
            if next_el.tag == 'mixed-citation':
                next_other_els = next_el.getchildren()
                for next_other_el in next_other_els:
                    if next_other_el.tag == 'article-title':
                        parent = next_other_el.getparent()
                        previous = next_other_el.getprevious()
                        # We can't strip the root element!
                        if parent is None:
                            continue
                        # Append the text to previous tail (or parent text if no previous), ensuring newline if block level
                        if next_other_el.text and isinstance(next_other_el.tag, six.string_types):
                            if previous is None:
                                parent.text = (parent.text or '') + next_other_el.text
                            else:
                                previous.tail = (previous.tail or '') + next_other_el.text
                        # Append the tail to last child tail, or previous tail, or parent text, ensuring newline if block level
                        if next_other_el.tail:
                            if len(next_other_el):
                                last = next_other_el[-1]
                                last.tail = (last.tail or '') + next_other_el.tail
                            elif previous is None:
                                parent.text = (parent.text or '') + next_other_el.tail
                            else:
                                previous.tail = (previous.tail or '') + next_other_el.tail
                        index = parent.index(next_other_el)
                        parent[index:index + 1] = next_other_el[:]
    return document
