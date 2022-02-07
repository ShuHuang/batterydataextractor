import logging
import unittest
from batterydataextractor.doc import Document

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestPropertyDataCompound(unittest.TestCase):

    maxDiff = None

    def do_parse(self, input, expected):
        p = Document(input)
        p.add_models_by_names(["mp"])
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_mpc1(self):
        s = '4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic acid (Compound 67): mp 163-164° C.'
        expected = [
            {'PropertyData':
                 {'compound': {'Compound': {'names': ['4-Amino-3-chloro-6-(2,3,4-trifluorophenyl)pyridine-2-carboxylic']}},
                  'specifier': 'mp',
                  'value': '163-164 ° C'}}]
        self.do_parse(s, expected)

    def test_mpc2(self):
        s = '3-Bromo-2,6-dichloroaniline: mp 71-72° C.'
        expected = [
            {'PropertyData':
                 {'compound': {'Compound': {'names': ['3-Bromo-2,6-dichloroaniline']}},
                  'specifier': 'mp',
                  'value': '71-72 ° C'}}]
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()
