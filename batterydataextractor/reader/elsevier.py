# -*- coding: utf-8 -*-
"""
batterydataextractor.reader.elsevier

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Elsevier XML reader
"""
from ..scrape.clean import clean, Cleaner
from ..scrape.elsevier import fix_elsevier_xml_whitespace, els_xml_whitespace, els_clean_abstract
from ..doc.meta import MetaData
from .markup import XmlReader
from lxml import etree

# XML stripper that removes the tags around numbers in chemical formulas
strip_els_xml = Cleaner(strip_xpath='.//ce:inf | .//ce:italic | .//ce:bold | .//ce:formula | .//mml:* | .//ce:sup'
                                    '| .//ce:cross-ref | .//ce:cross-refs | .//ja:math ',
                        kill_xpath='.//ce:cross-ref//ce:sup | .//ce:table//ce:sup | .//ce:float-anchor| .//ce:hsp'
                                   '| .//ja:math ')


class ElsevierXmlReader(XmlReader):
    """Reader for Elsevier XML documents."""

    cleaners = [clean, fix_elsevier_xml_whitespace, els_xml_whitespace, els_clean_abstract, strip_els_xml]

    etree.FunctionNamespace("http://www.elsevier.com/xml/svapi/article/dtd").prefix = 'default'
    etree.FunctionNamespace("http://www.elsevier.com/xml/bk/dtd").prefix = 'bk'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/cals/dtd").prefix = 'cals'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/dtd").prefix = 'ce'
    etree.FunctionNamespace("http://www.elsevier.com/xml/ja/dtd").prefix = 'ja'
    etree.FunctionNamespace("http://www.w3.org/1998/Math/MathML").prefix = 'mml'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/struct-aff/dtd").prefix = 'sa'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/struct-bib/dtd").prefix = 'sb'
    etree.FunctionNamespace("http://www.elsevier.com/xml/common/table/dtd").prefix = 'tb'
    etree.FunctionNamespace("http://www.w3.org/1999/xlink").prefix = 'xlink'
    etree.FunctionNamespace("http://www.elsevier.com/xml/xocs/dtd").prefix = 'xocs'
    etree.FunctionNamespace("http://purl.org/dc/elements/1.1/").prefix = 'dc'
    etree.FunctionNamespace("http://purl.org/dc/terms/").prefix = 'dcterms'
    etree.FunctionNamespace("http://prismstandard.org/namespaces/basic/2.0/").prefix = 'prism'
    etree.FunctionNamespace("http://www.w3.org/2001/XMLSchema-instance").prefix = 'xsi'

    root_css = 'default|full-text-retrieval-response'
    title_css = 'dc|title, ce|title'
    heading_css = 'ce|section-title'
    abstract_css = 'ce|abstract'
    table_css = 'ce|table'
    metadata_css = 'xocs|meta'
    metadata_title_css = 'xocs|normalized-article-title'
    metadata_author_css = 'xocs|normalized-first-auth-surname'
    metadata_journal_css = 'xocs|srctitle'
    metadata_volume_css = 'xocs|vol-first, xocs|volume-list xocs|volume'
    metadata_issue_css = 'xocs|issns xocs|issn-primary-formatted'
    metadata_publisher_css = 'xocs|copyright-line'
    metadata_date_css = 'xocs|available-online-date, xocs|orig-load-date'
    metadata_firstpage_css = 'xocs|first-fp'
    metadata_lastpage_css = 'xocs|last-lp'
    metadata_doi_css = 'xocs|doi, xocs|eii'
    metadata_pii_css = 'xocs|pii-unformatted'
    reference_css = 'ce|cross-refs, ce|cross-ref'
    citation_css = 'ce|bib-reference'
    ignore_css = 'ce|acknowledgment, ce|correspondence, ce|author, ce|doi, ja|jid, ja|aid, ce|pii, ' \
                 'xocs|oa-sponsor-type, xocs|open-access, default|openaccess, ce|article-number,'\
                 'default|openaccessArticle, dc|format, dc|creator, dc|identifier,'\
                 'default|eid, default|pii, xocs|ref-info, default|scopus-eid, '\
                 'xocs|normalized-srctitle, ' \
                 'xocs|eid, xocs|hub-eid, xocs|normalized-first-auth-surname,' \
                 'xocs|normalized-first-auth-initial, xocs|refkeys,' \
                 'xocs|attachment-eid, xocs|attachment-type, mml|math, mml|mrow, ' \
                 'ja|jid, ce|given-name, ce|surname, ce|affiliation, ce|label, ' \
                 'ce|grant-sponsor, ce|grant-number, prism|copyright,' \
                 'xocs|pii-unformatted, xocs|ucs-locator, ce|copyright,' \
                 'prism|publisher, prism|*, xocs|copyright-line, xocs|cp-notice,' \
                 'dc|description, ce|table, ce|figure, default|coredata, default|objects, default|scopus-id, ' \
                 'ce|nomenclature, ce|formula, ce|conflict-of-interest, ce|acknowledgements, default|aid'

    url_prefix = 'https://sciencedirect.com/science/article/pii/'

    def detect(self, fstring, fname=None):
        """Elsevier document detection based on string found in xml"""
        if fname and not fname.endswith('.xml'):
            return False
        if b'xmlns="http://www.elsevier.com/xml/svapi/article/dtd"' in fstring:
            return True
        return False

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
        lastpage = self._css(self.metadata_lastpage_css, el)
        doi = self._css(self.metadata_doi_css, el)
        pdf_url = self._css(self.metadata_pdf_url_css, el)
        html_url = self._css(self.metadata_html_url_css, el)

        metadata = {
                '_title': title[0].text if title else None,
                '_authors': [i.text for i in authors] if authors else None,
                '_publisher': publisher[0].text if publisher else None,
                '_journal': journal[0].text if journal else None,
                '_date': date[0].text if date else None,
                '_language': language[0].text if language else None,
                '_volume': volume[0].text if volume else None,
                '_issue': issue[0].text if issue else None,
                '_firstpage': firstpage[0].text if firstpage else None,
                '_lastpage': lastpage[0].text if lastpage else None,
                '_doi': doi[0].text if doi else None,
                '_pdf_url': self.url_prefix + pdf_url[0].text if pdf_url else None,
                '_html_url': self.url_prefix + html_url[0].text if html_url else None
        }
        meta = MetaData(metadata)
        return [meta]
