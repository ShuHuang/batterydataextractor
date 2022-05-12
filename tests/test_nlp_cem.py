import unittest
from batterydataextractor.nlp import BertCemTagger, CemTagger
from batterydataextractor.doc import Document, Span


class TestBertCemTagger(unittest.TestCase):
    def test_false_pos(self):
        """Test the Chem BERT Tagger on a simple sentence."""
        dt = BertCemTagger()
        self.assertEqual(
            [
                (('UV-vis', 'JJ'), 'O'),
                (('spectrum', 'NN'), 'O'),
                (('of', 'IN'), 'O'),
                (('Coumarin', 'NN'), 'MAT')
            ],
            dt.tag([
                ('UV-vis', 'JJ'),
                ('spectrum', 'NN'),
                ('of', 'IN'),
                ('Coumarin', 'NN')
            ])
        )


class TestCemTagger(unittest.TestCase):
    """Test combined CemTagger."""

    def test_stoplist(self):
        """Test CemTagger removes words in stoplist, including words entirely made up of ignore prefix/suffix.
        GitHub issue #12.
        """
        ct = CemTagger()
        self.assertEqual([('LiFePO4', 'MAT')], ct.tag([('LiFePO4', 'NN')]))

    def test_cems_stoplist(self):
        """Test Document cems removes words in stoplist, ncluding words entirely made up of ignore prefix/suffix.
        GitHub issue #12.
        """
        self.assertEqual([Span('LiFePO4', 0, 7)], Document('LiFePO4 materials').cems)
        self.assertEqual([], Document('-aromatic').cems)
        self.assertEqual([], Document('non-aromatic').cems)


if __name__ == '__main__':
    unittest.main()
