# -*- coding: utf-8 -*-
"""
test_text_normalize
~~~~~~~~~
Test the text package.
"""
import logging
import unittest

from batterydataextractor.text.normalize import normalize


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestNormalization(unittest.TestCase):

    def test_normalize(self):
        """Test normalize function."""
        # Weird control characters
        self.assertEqual(u'The quick brown fox jumped', normalize(u'The\u0003 quick br\u0005own fo\u0008x jumped'))
        # Unusual whitespace characters
        self.assertEqual(u'The quick brown fox jumped', normalize(u'The\u00A0quick\u2000brown\u2008fox\u000Bjumped'))
        # u2024 instead of full stop
        self.assertEqual(u'www.bbc.co.uk', normalize(u'www\u2024bbc\u2024co\u2024uk'))


if __name__ == '__main__':
    unittest.main()
