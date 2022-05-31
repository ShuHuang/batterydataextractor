import logging
import unittest
from batterydataextractor.nlp import AbbreviationDetector
from batterydataextractor.doc import Paragraph, Document


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestAbbreviationDetection(unittest.TestCase):

    def test_abbr1(self):
        """Test the AbbreviationDetection on a simple sentence."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'HDAC')], [('LF: ', 'histone deacetylase')]),
            ad.detect(['as', 'histone', 'deacetylase', '(', 'HDAC', ')', 'inhibitor'])
        )

    def test_abbr2(self):
        """Test the AbbreviationDetection on a simple sentence."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'VPA')], [('LF: ', 'valproic acid')]),
            ad.detect(['The', 'aim', 'of', 'this', 'study', 'was', 'to', 'identify', 'valproic', 'acid', '(', 'VPA', ')'])
        )

    def test_abbr3(self):
        """Test the AbbreviationDetection on a simple sentence."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'THF')], [('LF: ', 'tetrahydrofuran')]),
            ad.detect(['THF', '=', 'tetrahydrofuran'])
        )

    def test_abbr4(self):
        """Test the AbbreviationDetection on a simple sentence."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'NAG')], [('LF: ', 'N-acetyl-β-glucosaminidase')]),
            ad.detect(['NAG', '(', 'N-acetyl-β-glucosaminidase', ')'])
        )

    def test_abbr5(self):
        """Test the AbbreviationDetection on a simple sentence."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'NAG')], [('LF: ', 'N-acetyl-β-glucosaminidase')]),
            ad.detect(['blood', 'urea', 'nitrogen', ',', 'N-acetyl-β-glucosaminidase', '(', 'NAG', ')', ','])
        )

    def test_equiv1(self):
        """Test the AbbreviationDetection where string equivalent is needed."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'CTAB')], [('LF: ', 'hexadecyltrimethylammonium bromide')]),
            ad.detect(['was', 'composed', 'of', 'hexadecyltrimethylammonium', 'bromide', '(', 'CTAB', ')', 'and'])
        )

    def test_equiv2(self):
        """Test the AbbreviationDetection where string equivalent is needed."""
        ad = AbbreviationDetector()
        self.assertEqual(
            ([('Abbr: ', 'MeOH')], [('LF: ', 'methanol')]),
            ad.detect(['was', 'mostly', 'neutral', 'in', 'methanol', '(', 'MeOH', ')'])
        )

    def test_document(self):
        elements = [
            Paragraph('''The consequences of global change on rivers include altered flow regime, and entrance of
                         compounds that may be toxic to biota. When water is scarce, a reduced dilution capacity may
                         amplify the effects of chemical pollution. Therefore, studying the response of natural
                         communities to compromised water flow and to toxicants is critical for assessing how global
                         change may affect river ecosystems. This work aims to investigate how an episode of drought
                         might influence the response of river biofilms to pulses of triclosan (TCS). The objectives
                         were to assess the separate and combined effects of simulated drought (achieved through
                         drastic flow alteration) and of TCS exposure on biofilms growing in artificial channels.'''),
        ]
        d = Document(*elements)
        self.assertEqual([[('Abbr: ', 'TCS')], [('LF: ', 'triclosan')], [('Abbr: ', 'TCS')]], d.abbreviation_definitions)


if __name__ == '__main__':
    unittest.main()
