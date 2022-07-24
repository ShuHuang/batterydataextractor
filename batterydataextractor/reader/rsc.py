# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.rsc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RSC reader
"""
import logging

from ..scrape.clean import clean, Cleaner
from ..scrape.rsc import rsc_html_whitespace, replace_rsc_img_chars, join_rsc_table_captions, rsc_clean_abstract
from .markup import HtmlReader

log = logging.getLogger(__name__)

# XML stripper that removes the tags around numbers in chemical formulas
strip_rsc_html = Cleaner(strip_xpath='.//b')


class RscHtmlReader(HtmlReader):
    """Reader for HTML documents from the RSC."""

    cleaners = [clean, rsc_html_whitespace, replace_rsc_img_chars, rsc_clean_abstract, join_rsc_table_captions, strip_rsc_html]

    root_css = 'html'
    title_css = 'h1, .title_heading'
    heading_css = 'h2, h3, h4, h5, h6, .a_heading, .b_heading, .c_heading, .c_heading_indent, .d_heading,' \
                  '.d_heading_indent'
    abstract_css = 'div[class="abstract"], p[class="abstract"]'
    citation_css = 'span[id^="cit"]'
    reference_css = 'small sup a, a[href^="#cit"], a[href^="#fn"], a[href^="#tab"]'
    ignore_css = '.table_caption + table, .left_head, sup span.sup_ref, small sup a, a[href^="#fn"], .PMedLink, ' \
                 'table, figure'

    def detect(self, fstring, fname=None):
        """"""
        if fname and not (fname.endswith('.html') or fname.endswith('.htm')):
            return False
        if b'meta name="citation_doi" content="10.1039' in fstring:
            return True
        return False
