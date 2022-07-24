# -*- coding: utf-8 -*-
"""
batterydataextractor.scrape.rsc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The Royal Society of Chemistry (RSC) web scraper. Please get the permission from RSC before web-scraping.
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
    RSC web-scraper
    """
    def __init__(self, url=None, max_wait_time=30, driver=None):
        """
        :param url: RSC search query url.
        :param max_wait_time: maximum waiting time for the scraper.
        :param driver: the Selenium driver (default: Chrome driver).
        """
        super().__init__()
        self.url = url
        self.max_wait_time = max_wait_time
        self.driver = driver

    def get_doi(self, query, page):
        """
        Get a list of dois from query massages and the exact page.
        :param query: the query text (e.g. battery materials)
        :param page: the number of page
        :return: a list of dois of the relevant query text and page.
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
        next_button = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[class^=paging__btn]")))[1]
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
        Download the html paper of the doi
        :param doi: doi of the paper
        :param file_location: the saving location
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
            name = result['online_date'].replace("/", "") + '_' + doi

        with open(file_location + name + '.html', 'wb') as f:
            f.write(web_content)
        return

    @staticmethod
    def get_rsc_abstract(web_content):
        """
        Get the metadata and abstract from a rsc html file
        :param web_content: rsc html content
        :return: a dictionary of metadata and abstract
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
            if i.has_attr("name"):
                if i["name"] == "citation_online_date":
                    online_date = i['content']
        abstract = soup.find_all("p", attrs={"class": "abstract"})[0].get_text()
        return {"title": title, "doi": doi, "date": date, "journal": journal, "online_date": online_date,
                "abstract": abstract}


#: Map image URL components to unicode characters.
RSC_IMG_CHARS = {
    '2041': '^',              # caret
    '224a': '\u2248',         # almost equal
    'e001': '=',              # equals
    'e002': '\u2261',         # equivalent
    'e003': '\u2263',         # strictly equivalent
    'e006': '=',              # equals
    'e007': '\u2261',         # equivalent
    'e009': '>',              # greater than
    'e00a': '<',              # less than
    'e00c': '\u269f',         # three lines converging left
    'e00d': '\u269e',         # three lines converging right
    'e010': '\u250c',         # box down and right
    'e011': '\u2510',         # box down and left
    'e012': '\u2514',         # box up and right
    'e013': '\u2518',         # box up and left
    'e038': '\u2b21',         # white hexagon
    'e059': '\u25cd',         # ?
    'e05a': '\u25cd',         # ?
    'e069': '\u25a9',         # square with diagonal crosshatch fill
    'e077': '\u2b13',         # square with bottom half black
    'e082': '\u2b18',         # diamond with top half black
    'e083': '\u2b19',         # diamond with bottom half black
    'e084': '\u27d0',         # white diamond with centred do
    'e090': '\u2504',         # box drawings light triple dash horizontal (not exactly)
    'e091': '\u2504',         # box drawings light triple dash horizontal
    'e0a2': '\u03b3\u0307',   # small gamma with dot
    'e0b3': '\u03bc\u0342',   # small mu with circumflex
    'e0b7': '\u03c1\u0342',   # small rho with circumflex
    'e0c2': '\u03b1\u0305',   # small alpha with macron
    'e0c3': '\u03b2\u0305',   # small beta with macron
    'e0c5': '\u03b4\u0305',   # small delta with macron
    'e0c6': '\u03b5\u0305',   # small epsilon with macron
    'e0ce': 'v\u0305',        # small v with macron
    'e0c9': '\u03b8\u0305',   # small theta with macron
    'e0cb': '\u03ba\u0305',   # small kappa with macron
    'e0cc': '\u03bb\u0305',   # small lambda with macron
    'e0cd': '\u03bc\u0305',   # small mu with macron
    'e0d1': '\u03c1\u0305',   # small rho with macron
    'e0d4': '\u03c4\u0305',   # small tau with macron
    'e0d5': '\u03bd\u0305',   # small nu with macron
    'e0d6': '\u03d5\u0305',   # small phi with macron (stroked)
    'e0d7': '\u03c6\u0305',   # small phi with macron
    'e0d8': '\u03c7\u0305',   # small chi with macron
    'e0da': '\u03bd\u0305',   # small omega with macron
    'e0db': '\u03a6\u0303',   # capital phi with tilde
    'e0dd': '\u03b3\u0303',   # small lambda with tilde
    'e0de': '\u03b5\u0303',   # small epsilon with tilde
    'e0e0': '\u03bc\u0303',   # small mu with tilde
    'e0e1': 'v\u0303',        # small v with tilde
    'e0e4': '\u03c1\u0303',   # small rho with tilde
    'e0e7': '\u03b5\u20d7',   # small epsilon with rightwards arrow above
    'e0e9': '\u03bc\u20d7',   # small mu with rightwards arrow above
    'e0eb': '\u29b5',         # circle with horizontal bar
    'e0ec': '|',              # ? http://www.rsc.org/images/entities/char_e0ec.gif
    'e0ed': '|',              # ? http://www.rsc.org/images/entities/char_e0ed.gif
    'e0ee': '3/2',            # 3/2
    'e0f1': '\U0001d302',     # ?
    'e0f5': '\u03bd',         # small nu
    'e0f6': '\u27ff',         # long rightwards squiggle arrow
    'e100': '\u2506',         # box drawings light triple dash vertical
    'e103': '\u2605',         # Black Star
    'e107': '\u03b5\u0342',   # small epsilon with circumflex
    'e108': '\u03b7\u0342',   # small eta with circumflex
    'e109': '\u03ba\u0342',   # small kappa with circumflex
    'e10d': '\u03c3\u0303',   # small sigma with tilde
    'e110': '\u03b7\u0303',   # small eta with tilde
    'e112': '\U0001d4a2',     # script G
    'e113': '\U0001d219',     # ? greek vocal notation symbol-51
    'e116': '\u2933',         # wave arrow pointing directly right
    'e117': '\u2501',         # box drawings heavy horizontal
    'e11a': '\u03bb\u0342',   # small lambda with circumflex
    'e11b': '\u03c7\u0303',   # small chi with tilde
    'e11f': '5/2',            # 5/2
    'e120': '5/4',            # 5/4
    'e124': '\u2b22',         # black hexagon
    'e131': '\u03bd\u0303',   # small nu with tilde
    'e132': '\u0393\u0342',   # capital gamma with circumflex
    'e13d': '\u2b1f',         # black pentagon
    'e142': '\u210b',         # script capital H
    'e144': '\u2112',         # script capital L
    'e146': '\u2113',         # script small l
    'e170': '\U0001d544',     # double-struck capital M
    'e175': '\u211d',         # double-struck capital R
    'e177': '\U0001d54b',     # double-struck capital T
    'e17e': '\U0001D580',     # fraktur bold capital U
    'e18f': '\U0001d57d',     # fraktur bold capital R
    'e1c0': '\u2b21',         # white hexagon
    'e520': '\U0001d49c',     # script capital A
    'e523': '\U0001d49f',     # script capital D
    'e529': '\U0001d4a5',     # script capital J
    'e52d': '\U0001d4a9',     # script capital N
    'e52f': '\U0001d4ab',     # script capital P
    'e531': '\u211b',         # script capital R
    'e533': '\U0001d4af',     # script capital T
}


def rsc_html_whitespace(document):
    """ Remove whitespace in xml.text or xml.tails for all elements, if it is only whitespace """
    # selects all tags and checks if the text or tail are spaces
    for el in document.xpath('//*'):
        if el.tag == 'b':
            continue
        if str(el.text).isspace():
            el.text = ''
        if str(el.tail).isspace():
            el.tail = ''
        if el.text:
            el.text = el.text.replace('\n', ' ')
    return document


def join_rsc_table_captions(document):
    """Add wrapper tag around Tables and their respective captions
    Arguments:
        document {[type]} -- [description]
    """
    for el in document.xpath('//div[@class="table_caption"]'):
        next_el = el.getnext()
        if next_el.tag == 'div' and next_el.attrib['class'] == 'rtable__wrapper':
            caption_el = el
            table_el = next_el
            table_el.insert(0, caption_el)
    return document


def replace_rsc_img_chars(document):
    """Replace image characters with unicode equivalents."""
    image_re = re.compile('http://www.rsc.org/images/entities/(?:h[23]+_)?(?:[ib]+_)?char_([0-9a-f]{4})(?:_([0-9a-f]{4}))?\.gif')
    for img in document.xpath('.//img[starts-with(@src, "http://www.rsc.org/images/entities/")]'):
        m = image_re.match(img.get('src'))
        if m:
            u1, u2 = m.group(1), m.group(2)
            if not u2 and u1 in RSC_IMG_CHARS:
                rep = RSC_IMG_CHARS[u1]
            else:
                rep = ('\\u%s' % u1).encode('ascii').decode('unicode-escape')
                if u2:
                    rep += ('\\u%s' % u2).encode('ascii').decode('unicode-escape')
            if img.tail is not None:
                rep += img.tail  # Make sure we don't remove any tail text
            parent = img.getparent()
            if parent is not None:
                previous = img.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + rep
                else:
                    parent.text = (parent.text or '') + rep
                parent.remove(img)
    return document


def rsc_clean_abstract(document):
    """ Remove <h2> in abstract"""
    # selects all tags and checks if the text or tail are spaces
    for el in document.xpath('//div[@class="abstract"] | //p[@class="abstract"]'):
        next_els = el.getchildren()
        for next_el in next_els:
            if next_el.tag == 'h2':
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
