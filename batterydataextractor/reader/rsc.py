# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.rsc

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RSC reader
author:
"""
import logging
import re

from ..scrape.clean import clean, Cleaner
from .markup import HtmlReader

log = logging.getLogger(__name__)

# XML stripper that removes the tags around numbers in chemical formulas
strip_rsc_html = Cleaner(strip_xpath='.//b')

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


class RscHtmlReader(HtmlReader):
    """Reader for HTML documents from the RSC."""

    cleaners = [clean, rsc_html_whitespace, replace_rsc_img_chars, join_rsc_table_captions, strip_rsc_html]

    root_css = 'html'
    title_css = 'h1, .title_heading'
    heading_css = 'h2, h3, h4, h5, h6, .a_heading, .b_heading, .c_heading, .c_heading_indent, .d_heading, .d_heading_indent'
    citation_css = 'span[id^="cit"]'
    table_css = 'div[class^="rtable__wrapper"]'
    table_caption_css = '.table_caption'
    table_head_row_css = 'table thead tr'
    table_body_row_css = 'table tbody tr'
    table_footnote_css = 'table tfoot tr th .sup_inf'
    reference_css = 'small sup a, a[href^="#cit"], a[href^="#fn"], a[href^="#tab"]'
    figure_css = '.image_table'
    figure_caption_css = '.graphic_title'
    ignore_css = '.table_caption + table, .left_head, sup span.sup_ref, small sup a, a[href^="#fn"], .PMedLink'

    def detect(self, fstring, fname=None):
        """"""
        if fname and not (fname.endswith('.html') or fname.endswith('.htm')):
            return False
        if b'meta name="citation_doi" content="10.1039' in fstring:
            return True
        return False
