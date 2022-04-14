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
                (('Coumarin', 'NN'), 'B-MAT')
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
        self.assertEqual([(('benzene-aromatic', 'NN'), 'B-MAT')], ct.tag([('benzene-aromatic', 'NN')]))
        self.assertEqual([(('-aromatic', 'JJ'), None)], ct.tag([('-aromatic', 'JJ')]))
        self.assertEqual([(('non-aromatic', 'JJ'), None)], ct.tag([('non-aromatic', 'JJ')]))

    def test_cems_stoplist(self):
        """Test Document cems removes words in stoplist, ncluding words entirely made up of ignore prefix/suffix.
        GitHub issue #12.
        """
        self.assertEqual([Span('benzene', 0, 7)], Document('benzene-aromatic').cems)
        self.assertEqual([], Document('-aromatic').cems)
        self.assertEqual([], Document('non-aromatic').cems)


if __name__ == '__main__':
    unittest.main()
