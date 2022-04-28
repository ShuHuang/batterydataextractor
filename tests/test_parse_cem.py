import logging
import unittest

from batterydataextractor.doc.document import Document
from batterydataextractor.doc.text import Heading, Paragraph

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestParseHeading(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        s = Heading(input)
        log.debug(s)
        log.debug(s.tagged_tokens)
        results = [r.serialize() for r in s.records]
        log.debug(results)
        log.debug(expected)
        log.debug(results == expected)
        self.assertEqual(expected, results)

    def test_preparation_of(self):
        s = 'Preparation of 4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic (Compound 41)'
        expected = [
            {'Compound': {'names': ['4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic']}}
        ]
        self.do_parse(s, expected)

    def test_background(self):
        """Ensure uppercase heading isn't recognised (as a likely abbreviation)"""
        s = 'BACKGROUND'
        expected = []
        self.do_parse(s, expected)

    def test_background_art(self):
        """Ensure uppercase heading isn't recognised (as a likely abbreviation)"""
        s = 'BACKGROUND ART'
        expected = []
        self.do_parse(s, expected)

    def test_name1(self):
        s = '4-[4-(4-[5-[5-(4-Hydroxyphenyl)-3-phenyl-1H-pyrrol-2-ylimino]-4-phenyl-5H-pyrrol-2-yl]-phenoxymethyl)-[1,2,3]triazol-1-yl]butyric (8b)'
        expected = [{'Compound': {'names': ['4-[4-(4-[5-[5-(4-Hydroxyphenyl)-3-phenyl-1H-pyrrol-2-ylimino]-4-phenyl-5H-pyrrol-2-yl]-phenoxymethyl)-[1,2,3]triazol-1-yl]butyric']}}]
        self.do_parse(s, expected)

    def test_fluorescent_nano_beads(self):
        """"""
        s = 'Fluorescent Nano-Beads'
        expected = []
        self.do_parse(s, expected)

    def test_test(self):
        """"""
        s = 'Test 2'
        expected = []
        self.do_parse(s, expected)

    def test_name2(self):
        """"""
        s = '1-(3,4-Dibenzyloxycinnamoyl)-3,4′-dibenzyloxyresveratrol (14):'
        expected = [{'Compound': {'names': [u'1-(3,4-Dibenzyloxycinnamoyl)-3,4\u2032-dibenzyloxyresveratrol']}}]
        self.do_parse(s, expected)

    def test_name3(self):
        """"""
        s = '3.2 [3-(2-p-Tolylimidazo[1,2-a]pyridin-6-yl)phenyl]methanol'
        expected = [{'Compound': {'names': [u'[3-(2-p-Tolylimidazo[1,2-a]pyridin-6-yl)phenyl]methanol']}}]
        self.do_parse(s, expected)

    def test_name4(self):
        """"""
        s = 'Preparation of (E)-1-(4-(benzyloxy)phenyl)-2-(3,5-bis(benzyloxy)phenyl)ethene (I)'
        expected = [{'Compound': {'names': [u'(E)-1-(4-(benzyloxy)phenyl)-2-(3,5-bis(benzyloxy)phenyl)ethene']}}]
        self.do_parse(s, expected)

    def test_name5(self):
        """"""
        s = 'Preparation of 2-(10-bromoanthracene-9-yl)thiophene, 11'
        expected = [{'Compound': {'names': ['2-(10-bromoanthracene-9-yl)thiophene']}}]
        self.do_parse(s, expected)


class TestParseDocument(unittest.TestCase):

    maxDiff = None

    def test_consecutive_headings(self):
        d = Document(
            Heading('Preparation of 2-Amino-3-methoxy-5-chloropyridine'),
            Heading('Example 3'),
            Paragraph('The solid is suspended in hexanes, stirred and filtered to give the product as a bright yellow solid. (MP 93-94\xc2\xb0 C.).')
        )
        results = [r.serialize() for r in d.records]
        self.assertEqual(results, [{'Compound': {'names': [u'2-Amino-3-methoxy-5-chloropyridine']}},
                                   {'Compound': {'names': [u'hexanes']}}])


if __name__ == '__main__':
    unittest.main()
