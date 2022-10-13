# -*- coding: utf-8 -*-
"""
test_reader_rsc
~~~~~~~~~~~~~~~
Test RSC reader.
"""
import io
import logging
import os
import unittest

from batterydataextractor.doc import Document
from batterydataextractor.reader import RscHtmlReader


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestRscHtmlReader(unittest.TestCase):

    maxDiff = None

    def test_detect(self):
        """Test RscHtmlReader can detect an RSC document."""
        r = RscHtmlReader()
        fname = 'rsc_test1.html'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        content = f.read()
        self.assertEqual(r.detect(content, fname=fname), True)

    def test_direct_usage(self):
        """Test RscHtmlReader used directly to parse file."""
        r = RscHtmlReader()
        fname = 'rsc_test1.html'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        content = f.read()
        d = r.readstring(content)
        self.assertEqual(len(d.elements), 95)

    def test_document_usage(self):
        """Test RscHtmlReader used via Document.from_file."""
        fname = 'rsc_test2.html'
        f = io.open(os.path.join(os.path.dirname(__file__), 'testpapers', fname), 'rb')
        d = Document.from_file(f, readers=[RscHtmlReader()])
        self.assertEqual(len(d.elements), 60)
        self.assertEqual(d.metadata[0].title, 'Surface modification of electrospun TiO 2 nanofibers via layer-by-layer self-assembly for high-performance lithium-ion batteries  ')
        self.assertEqual(d.headdata, [])

if __name__ == '__main__':
    unittest.main()
