import logging
import unittest
from batterydataextractor.nlp import ChemSentenceTokenizer
from batterydataextractor.doc import Text


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestChemSentenceTokenizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ps = ChemSentenceTokenizer()

    def test_sentence_tokenizer(self):
        """Test the Sentence Tokenizer directly."""
        text = 'This is the first sentence. This is another. This is a third.'
        sents = ['This is the first sentence.', 'This is another.', 'This is a third.']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_et_al(self):
        """Test the tokenizer handles et al. within a sentence correctly."""
        text = 'Costa et al. reported the growth of HA nanowires due to the chemical potential of an amorphous calcium phosphate solution. This structural feature would make the {001} very sensitive to surrounding growth conditions.'
        sents = [
            'Costa et al. reported the growth of HA nanowires due to the chemical potential of an amorphous calcium phosphate solution.',
            'This structural feature would make the {001} very sensitive to surrounding growth conditions.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_et_al2(self):
        """Test the tokenizer handles et al. abbreviation correctly."""
        text = 'In the field of DSCs, Gratzel et al. demonstrated this for the first time in 2004.'
        sents = ['In the field of DSCs, Gratzel et al. demonstrated this for the first time in 2004.']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_fig_bracket(self):
        """Test the tokenizer handles bracketed Fig. abbreviation correctly."""
        text = 'The model is in good agreement with the intensity of the peaks observed in the XRD patterns (Fig. 1).'
        sents = ['The model is in good agreement with the intensity of the peaks observed in the XRD patterns (Fig. 1).']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_eg_et_al(self):
        """Test the tokenizer handles e.g. and et al. abbreviations correctly."""
        text = 'There is a clear linkage to some diseases, e.g. multiple myeloma. Vidler et al. studied the druggability of the different members, but to date there are no PCM studies performed on this family.'
        sents = [
            'There is a clear linkage to some diseases, e.g. multiple myeloma.',
            'Vidler et al. studied the druggability of the different members, but to date there are no PCM studies performed on this family.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_colon(self):
        """Test the tokenizer handles colons correctly."""
        text = 'The authors were able to split this into two types, namely: those involved in absorption and those involved in emission.'
        sents = ['The authors were able to split this into two types, namely: those involved in absorption and those involved in emission.']
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_lowercase_sentence_start(self):
        """Test the tokenizer handles lowercase sentence start correctly."""
        text = 'These regions are positive contributors to overall efficiency. van Westen et al. built on this by including data from 24 new sources.'
        sents = [
            'These regions are positive contributors to overall efficiency.',
            'van Westen et al. built on this by including data from 24 new sources.'
        ]
        self.assertEqual(sents, self.ps.tokenize(text))

    def test_chemtext_sentence(self):
        """Test sentence tokenization through the ChemText and Sentence API."""
        t = Text('These regions are positive contributors to overall efficiency. van Westen et al. built on this by including data from 24 new sources.')
        self.assertEqual(
            [(0, 62, 'These regions are positive contributors to overall efficiency.'), (63, 133, 'van Westen et al. built on this by including data from 24 new sources.')],
            [(s.start, s.end, s.text) for s in t.sentences]
        )


if __name__ == '__main__':
    unittest.main()
