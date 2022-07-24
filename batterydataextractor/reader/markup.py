# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.markup

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
XML and HTML readers based on lxml.
"""
import logging
import six
from abc import abstractmethod, ABCMeta
from collections import defaultdict

from lxml import etree
from lxml.etree import XMLParser
from lxml.html import HTMLParser

from ..errors import ReaderError
from ..doc.document import Document
from ..doc.text import Title, Heading, Paragraph, Citation, Text, Sentence, Abstract
from ..doc.meta import MetaData
from ..scrape.clean import clean
from ..scrape.csstranslator import CssHTMLTranslator
from .base import BaseReader
from ..text import get_encoding


log = logging.getLogger(__name__)

#: Inline level HTML elements
INLINE_ELEMENTS = {
    'b', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'cite', 'code', 'dfn', 'em', 'kbd', 'strong', 'samp', 'var',
    'a', 'bdo', 'br', 'img', 'map', 'object', 'q', 'script', 'span', 'sub', 'sup', 'button', 'input', 'label',
    'select', 'textarea', 'blink', 'font', 'marquee', 'nobr', 's', 'strike', 'u', 'wbr',
}


class LxmlReader(six.with_metaclass(ABCMeta, BaseReader)):
    """Abstract base class for lxml-based readers."""

    #: A ``Cleaner`` instance to
    cleaners = [clean]

    root_css = 'html'
    title_css = 'h1'
    heading_css = 'h2, h3, h4, h5, h6'
    reference_css = 'a.ref'
    citation_css = 'cite'
    abstract_css = 'div[class="abstract"], p[class="abstract"]'

    metadata_css = 'head'
    metadata_publisher_css = 'meta[name="DC.publisher"]::attr("content"), meta[name="citation_publisher"]::attr("content")'
    metadata_author_css = 'meta[name="DC.Creator"]::attr("content"), meta[name="citation_author"]::attr("content")'
    metadata_title_css = 'meta[name="DC.title"]::attr("content"), meta[name="citation_title"]::attr("content")'
    metadata_date_css = 'meta[name="DC.Date"]::attr("content"), meta[name="citation_date"]::attr("content"), meta[name="citation_online_date"]::attr("content")'
    metadata_doi_css = 'meta[name="DC.Identifier"]::attr("content"), meta[name="citation_doi"]::attr("content")'
    metadata_language_css = 'meta[name="DC.Language"]::attr("content"), meta[name="citation_language"]::attr("content")'
    metadata_journal_css = 'meta[name="citation_journal_title"]::attr("content")'
    metadata_volume_css = 'meta[name="citation_volume"]::attr("content")'
    metadata_issue_css = 'meta[name="citation_issue"]::attr("content")'
    metadata_firstpage_css = 'meta[name="citation_firstpage"]::attr("content")'
    metadata_lastpage_css = 'meta[name="citation_lastpage"]::attr("content")'
    metadata_pdf_url_css = 'meta[name="citation_pdf_url"]::attr("content")'
    metadata_html_url_css = 'meta[name="citation_fulltext_html_url"]::attr("content"), meta[name="citation_abstract_html_url"]::attr("content")'

    ignore_css = 'a.ref sup'

    #: Inline elements
    inline_elements = INLINE_ELEMENTS

    def _parse_element_r(self, el, specials, refs, id=None, element_cls=Paragraph):
        """Recursively parse HTML/XML element and its children into a list of Document elements."""
        elements = []
        if el.tag in {etree.Comment, etree.ProcessingInstruction}:
            return []
        # if el in refs:
            # return [element_cls('', references=refs[el])]
        if el in specials:
            return specials[el]
        id = el.get('id', id)
        references = refs.get(el, [])
        if el.text is not None:
            elements.append(element_cls(six.text_type(el.text), id=id, references=references))
        elif references:
            elements.append(element_cls('', id=id, references=references))
        for child in el:
            # br is a special case - technically inline, but we want to split
            if child.tag not in {etree.Comment, etree.ProcessingInstruction} and child.tag.lower() == 'br':
                elements.append(element_cls(''))

            child_elements = self._parse_element_r(child, specials=specials, refs=refs, id=id, element_cls=element_cls)
            if (self._is_inline(child) and len(elements) > 0 and len(child_elements) > 0 and
                    isinstance(elements[-1], (Text, Sentence)) and isinstance(child_elements[0], (Text, Sentence)) and
                    type(elements[-1]) == type(child_elements[0])):
                elements[-1] += child_elements.pop(0)
            elements.extend(child_elements)
            if child.tail is not None:
                if self._is_inline(child) and len(elements) > 0 and isinstance(elements[-1], element_cls):
                    elements[-1] += element_cls(six.text_type(child.tail), id=id)
                else:
                    elements.append(element_cls(six.text_type(child.tail), id=id))
        return elements

    def _parse_element(self, el, specials=None, refs=None, element_cls=Paragraph):
        """"""
        if specials is None:
            specials = {}
        if refs is None:
            refs = {}
        elements = self._parse_element_r(el, specials=specials, refs=refs, element_cls=element_cls)
        final_elements = []
        for element in elements:
            # Filter empty text elements
            if isinstance(element, Text):
                if element.text.strip():
                    final_elements.append(element)
            else:
                final_elements.append(element)
        return final_elements

    def _parse_text(self, el, refs=None, specials=None,  element_cls=Paragraph):
        """Like _parse_element but ensure a single element."""
        if specials is None:
            specials = {}
        if refs is None:
            refs = {}
        elements = self._parse_element_r(el, specials=specials, refs=refs, element_cls=element_cls)
        # This occurs if the input element is self-closing... (some table td in NLM XML)
        if not elements:
            return [element_cls('')]
        element = elements[0]
        for next_element in elements[1:]:
            try:
                element += element_cls(' ') + next_element
            except TypeError as e:
                continue
                log.warning('Adding of two objects was skipped. {} and {} cannot be added.'.format(str(type(element)), str(type(next_element))))
        return [element]

    @staticmethod
    def _parse_reference(el):
        """Return reference ID from href or text content."""
        if '#' in el.get('href', ''):
            return [el.get('href').split('#', 1)[1]]
        elif 'rid' in el.attrib:
            return [el.attrib['rid']]
        elif 'idref' in el.attrib:
            return [el.attrib['idref']]
        else:
            return [''.join(el.itertext()).strip()]

    def _parse_metadata(self, el, refs, specials):
        title = self._css(self.metadata_title_css, el)
        authors = self._css(self.metadata_author_css, el)
        publisher = self._css(self.metadata_publisher_css, el)
        journal = self._css(self.metadata_journal_css, el)
        date = self._css(self.metadata_date_css, el)
        language = self._css(self.metadata_language_css, el)
        volume = self._css(self.metadata_volume_css, el)
        issue = self._css(self.metadata_issue_css, el)
        firstpage = self._css(self.metadata_firstpage_css, el)
        lastpage= self._css(self.metadata_lastpage_css, el)
        doi = self._css(self.metadata_doi_css, el)
        pdf_url = self._css(self.metadata_pdf_url_css, el)
        html_url = self._css(self.metadata_html_url_css, el)

        metadata = {
                '_title': title[0] if title else None,
                '_authors': authors if authors else None,
                '_publisher': publisher[0] if publisher else None,
                '_journal': journal[0] if journal else None,
                '_date': date[0] if date else None,
                '_language': language[0] if language else None,
                '_volume': volume[0] if volume else None,
                '_issue': issue[0] if issue else None,
                '_firstpage': firstpage[0] if firstpage else None,
                '_lastpage': lastpage[0] if lastpage else None,
                '_doi': doi[0] if doi else None,
                '_pdf_url': pdf_url[0] if pdf_url else None,
                '_html_url': html_url[0] if html_url else None
                }
        meta = MetaData(metadata)
        return [meta]

    @staticmethod
    def _xpath(query, root):
        result = root.xpath(query, smart_strings=False)
        if type(result) is not list:
            result = [result]
        log.debug('Selecting XPath: {}: {}'.format(query, result))
        return result

    def _css(self, query, root):
        return self._xpath(CssHTMLTranslator().css_to_xpath(query), root)

    def _is_inline(self, element):
        """Return True if an element is inline."""
        if element.tag not in {etree.Comment, etree.ProcessingInstruction} and element.tag.lower() in self.inline_elements:
            return True
        return False

    @abstractmethod
    def _make_tree(self, fstring):
        """Read a string into an lxml elementtree."""
        pass

    def parse(self, fstring):
        root = self._make_tree(fstring)
        self.root = root

        if root is None:
            raise ReaderError
        root = self._css(self.root_css, root)[0]
        for cleaner in self.cleaners:
            cleaner(root)
        specials = {}
        refs = defaultdict(list)
        titles = self._css(self.title_css, root)
        headings = self._css(self.heading_css, root)
        abstracts = self._css(self.abstract_css, root)
        citations = self._css(self.citation_css, root)
        references = self._css(self.reference_css, root)
        ignores = self._css(self.ignore_css, root)
        metadata = self._css(self.metadata_css, root)
        for reference in references:
            refs[reference.getparent()].extend(self._parse_reference(reference))
        for title in titles:
            specials[title] = self._parse_text(title, element_cls=Title, refs=refs, specials=specials)
        for heading in headings:
            specials[heading] = self._parse_text(heading, element_cls=Heading, refs=refs, specials=specials)
        for citation in citations:
            specials[citation] = self._parse_text(citation, element_cls=Citation, refs=refs, specials=specials)
        for md in metadata:
            specials[md] = self._parse_metadata(md, refs=refs, specials=specials)
        for abstract in abstracts:
            specials[abstract] = self._parse_text(abstract, element_cls=Abstract, refs=refs, specials=specials)
        for ignore in ignores:
            specials[ignore] = []
        elements = self._parse_element(root, specials=specials, refs=refs)
        return Document(*elements)


class XmlReader(LxmlReader):
    """Reader for generic XML documents."""

    def detect(self, fstring, fname=None):
        """"""
        if fname and not fname.endswith('.xml'):
            return False
        return True

    def _make_tree(self, fstring):
        root = etree.fromstring(fstring, parser=XMLParser(recover=True, encoding=get_encoding(fstring)))
        return root


class HtmlReader(LxmlReader):
    """Reader for generic HTML documents."""

    def detect(self, fstring, fname=None):
        """"""
        if fname and not (fname.endswith('.html') or fname.endswith('.htm')):
            return False
        return True

    def _make_tree(self, fstring):
        root = etree.fromstring(fstring, parser=HTMLParser(encoding=get_encoding(fstring)))
        return root
