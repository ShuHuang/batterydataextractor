import unittest
from batterydataextractor.nlp import BertTagger


class TestBertTagger(unittest.TestCase):
    """Test BertTagger."""

    @classmethod
    def setUpClass(cls):
        cls.t = BertTagger()

    def test_tag_simple(self):
        """Test the ChemApPosTagger  on a simple sentence."""
        self.assertEqual(
            [('And', 'CC'), ('now', 'RB'), ('for', 'IN'), ('something', 'NN'), ('completely', 'NNP'), ('different', 'JJ')],
            self.t.tag(['And', 'now', 'for', 'something', 'completely', 'different'])
        )

    # def test_text_sentence(self):
    #     """Test tagging through the Text and Sentence API."""
    #     t = Text('And now for something completely different')
    #     self.assertEqual(
    #         [[(u'And', u'CC'), (u'now', u'RB'), (u'for', u'IN'), (u'something', u'NN'), (u'completely', u'RB'), (u'different', u'JJ')]],
    #         t.pos_tagged_tokens
    #     )


if __name__ == '__main__':
    unittest.main()
