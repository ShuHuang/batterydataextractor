# -*- coding: utf-8 -*-
"""
test_reader_springer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test reader for Springer.
"""
import unittest
import logging
import io
import os

from batterydataextractor.doc.document import Document
from batterydataextractor.reader.springer import SpringerXmlReader

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestSpringerXMLReader(unittest.TestCase):

    maxDiff = None

    def test_detect(self):
        """Test RscXMLReader can detect an RSC document."""
        r = SpringerXmlReader()
        fname = 'spr_test1.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        content = f.read()
        f.close()
        self.assertEqual(r.detect(content, fname=fname), True)

    def test_direct_usage(self):
        """Test RscXMLReader used directly to parse file."""
        r = SpringerXmlReader()
        fname = 'spr_test1.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        content = f.read()
        d = r.readstring(content)
        f.close()
        self.assertEqual(len(d.elements), 279)

    def test_document_usage(self):
        """Test RscXMLReader used via Document.from_file."""
        fname = 'spr_test2.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        d = Document.from_file(f, readers=[SpringerXmlReader()])
        self.assertEqual(len(d.elements), 60)
        self.assertEqual(d.metadata[0].authors, ['Hua-Chao Tao', 'Xue-Lin Yang', 'Lu-Lu Zhang', 'Shi-Bing Ni'])
        self.assertEqual(d.headdata, [])


if __name__ == '__main__':
    unittest.main()
