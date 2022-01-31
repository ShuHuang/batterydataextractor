# -*- coding: utf-8 -*-
"""
test_reader_elsevier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Test reader for Elsevier.
"""
import unittest
import logging
import io
import os

from batterydataextractor.doc.document import Document
from batterydataextractor.reader.elsevier import ElsevierXmlReader

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestElsXMLReader(unittest.TestCase):

    maxDiff = None

    def test_detect(self):
        """Test RscXMLReader can detect an RSC document."""
        r = ElsevierXmlReader()
        fname = 'els_test1.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        content = f.read()
        f.close()
        self.assertEqual(r.detect(content, fname=fname), True)

    def test_direct_usage(self):
        """Test RscXMLReader used directly to parse file."""
        r = ElsevierXmlReader()
        fname = 'els_test1.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        content = f.read()
        d = r.readstring(content)
        f.close()
        self.assertEqual(len(d.elements), 143)

    def test_document_usage(self):
        """Test RscXMLReader used via Document.from_file."""
        fname = 'els_test2.xml'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        d = Document.from_file(f, readers=[ElsevierXmlReader()])
        self.assertEqual(len(d.elements), 56)


if __name__ == '__main__':
    unittest.main()
