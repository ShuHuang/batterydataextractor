# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.springer

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Springer XML reader
author: Shu Huang
"""
from ..scrape.clean import clean, Cleaner
from ..scrape.elsevier import fix_elsevier_xml_whitespace, els_xml_whitespace
from ..doc.meta import MetaData
from .markup import XmlReader
from lxml import etree

# XML stripper that removes the tags around numbers in chemical formulas
strip_spr_xml = Cleaner(strip_xpath='.//ce:inf',
                        kill_xpath='.//ce:cross-ref//ce:sup')


class SpringerXmlReader(XmlReader):
    """Reader for Springer XML documents."""

    cleaners = [clean]
    # cleaners = [clean, fix_elsevier_xml_whitespace, els_xml_whitespace, strip_els_xml]

    root_css = 'response'
    title_css = 'article-title'
    heading_css = 'title'
    reference_css = 'xref'
    citation_css = 'ref'
    abstract_css = 'abstract'
    # table_css = 'ce|table'

    # metadata_css = 'front'
    # metadata_title_css = 'article-title'
    # metadata_author_css = 'surname'
    # metadata_journal_css = 'journal-title'
    # metadata_volume_css = 'volume'
    # metadata_issue_css = 'issue'
    # metadata_publisher_css = 'publisher-name'
    # metadata_date_css = 'pub-date'
    # metadata_firstpage_css = 'fpage'
    # metadata_lastpage_css = 'lpage'
    # metadata_doi_css = 'article-id[pub-id-type="doi"]'

    ignore_css = ''

    def detect(self, fstring, fname=None):
        """Springer document detection based on string found in xml"""
        if fname and not fname.endswith('.xml'):
            return False
        if b'dtd-version="1.2"' in fstring:
            return True
        return False

    def _parse_metadata(self, el, refs, specials):
        return []
        # title = self._css(self.metadata_title_css, el)
        # authors = self._css(self.metadata_author_css, el)
        # publisher = self._css(self.metadata_publisher_css, el)
        # journal = self._css(self.metadata_journal_css, el)
        # date = self._css(self.metadata_date_css, el)
        # volume = self._css(self.metadata_volume_css, el)
        # issue = self._css(self.metadata_issue_css, el)
        # firstpage = self._css(self.metadata_firstpage_css, el)
        # lastpage = self._css(self.metadata_lastpage_css, el)
        # doi = self._css(self.metadata_doi_css, el)

        # metadata = {
        #         '_title': title[0].text if title else None,
                # '_authors': [i.text for i in authors] if authors else None,
                # '_publisher': publisher[0].text if publisher else None,
                # '_journal': journal[0].text if journal else None,
                # '_date': date[0].text if date else None,
                # '_volume': volume[0].text if volume else None,
                # '_issue': issue[0].text if issue else None,
                # '_firstpage': firstpage[0].text if firstpage else None,
                # '_lastpage': lastpage[0].text if lastpage else None,
                # '_doi': doi[0].text if doi else None,
                # }
        # meta = MetaData(metadata)
        # return [meta]
