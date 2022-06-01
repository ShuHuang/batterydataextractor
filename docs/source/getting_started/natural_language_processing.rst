===========================
Natural Language Processing
===========================

BatteryDataExtractor also includes state-of-the-art Natural Language Processing (NLP) facilities, as described here.

Tokenization
-----------------

.. rubric:: Sentence Tokenization

Use the ``sentences`` property on a text-based document element to perform sentence segmentation. The sentence tokenizer is based on ``en_core_sci_sm`` package that is trained specifically on scientific text by SciPy::

    >>> from batterydataextractor.doc import Paragraph
    >>> para = Paragraph('The mechanism of lithium intercalation in the so-called ‘soft’ anodes, i.e. graphite or graphitable carbons, is well known. It develops through well-identified, reversible stages, corresponding to progressive intercalation within discrete graphene layers, to reach the formation of LiC6 with a maximum theoretical capacity of 372 ± 2.4 mAh g−1.')
    >>> para.sentences
    [Sentence('The mechanism of lithium intercalation in the so-called ‘soft’ anodes, i.e. graphite or graphitable carbons, is well known.', 0, 123),
     Sentence('It develops through well-identified, reversible stages, corresponding to progressive intercalation within discrete graphene layers, to reach the formation of LiC6 with a maximum theoretical capacity of 372 ± 2.4 mAh g−1.', 124, 344)]

Each sentence object is a document element in itself, and additionally contains the start and end character offsets within its parent element.

.. rubric:: Word Tokenization

Use the ``tokens`` property to get the word tokens::

    >>> para.tokens
    [[Token('The', 0, 3),
    Token('mechanism', 4, 13),
    Token('of', 14, 16),
    Token('lithium', 17, 24),
    Token('intercalation', 25, 38),
    Token('in', 39, 41),
    Token('the', 42, 45),
    Token('so', 46, 48),
    Token('-', 48, 49),
    ...
    ]]

    >>> para.sentences[0].tokens
    [Token('1,4-Dibromoanthracene', 0, 21),
     Token('was', 22, 25),
     Token('prepared', 26, 34),
     Token('from', 35, 39),
     Token('1,4-diaminoanthraquinone', 40, 64),
     Token('.', 64, 65)]

There are also ``raw_sentences`` and ``raw_tokens`` properties that return strings instead of ``Sentence`` and ``Token`` objects.

Part-of-speech Tagging
---------------------------

BatteryDataExtractor contains a chemistry-aware Part-of-speech tagger that is based on the fine-tuned base BERT-cased model. Use the ``pos_tagged_tokens`` property on a document element to get the tagged tokens::

    >>> s = Sentence('1H NMR spectra were recorded on a 300 MHz BRUKER DPX300 spectrometer.')
    >>> s.pos_tagged_tokens
    [('1H', 'CD'),
    ('NMR', 'NNP'),
    ('spectra', 'NN'),
    ('were', 'VBD'),
    ('recorded', 'VBN'),
    ('on', 'IN'),
    ('a', 'DT'),
    ('300', 'CD'),
    ('MHz', '.'),
    ('BRUKER', 'NNP'),
    ('DPX300', 'NNP'),
    ('spectrometer', 'NN'),
    ('.', '.')]

.. rubric:: Using Taggers Directly

All taggers have a ``tag`` method that takes a list of :class:`~chemdataextractor.doc.text.RichToken` instances and returns a list of (token, tag) tuples. For more information on how to use these taggers directly, see the documentation for :class:`~batterydataextractor.nlp.BaseTagger`.

Lexicon
------------

As BatteryDataExtractor processes documents, it adds each unique word that it encounters to the ``Lexicon`` as a ``Lexeme``.
Each ``Lexeme`` stores various word features, so they don't have to be re-calculated for every occurrence of that word.

You can access the Lexeme for a token using the ``lex`` property::

    >>> s = Sentence('Sulphur and Oxygen.')
    >>> s.tokens[0]
    Token('Sulphur', 0, 7)
    >>> s.tokens[0].lex.normalized
    'sulfur'
    >>> s.tokens[0].lex.is_hyphenated
    False

Abbreviation Detection
---------------------------

Abbreviation detection is based on the fine-tuned BatteryOnlyBERT-cased model::

    >>> p = Paragraph(u'Dye-sensitized solar cells (DSSCs) with ZnTPP = Zinc tetraphenylporphyrin.')
    >>> p.abbreviation_definitions
    [[('Abbr: ', 'DSSCs'), ('Abbr: ', 'ZnTPP')],
     [('LF: ', 'Dye - sensitized solar cells'),
      ('LF: ', 'Zinc tetraphenylporphyrin')]]

Chemical Named Entity Recognition (CNER)
----------------------------------------------

Chemical Named Entity Recognition (CNER) is based on the fine-tuned BatteryOnlyBERT-uncased model::

  >>> doc.cems
    [Span('lithium', 17, 24),
     Span('graphite', 76, 84),
     Span('carbons', 100, 107),
     Span('graphene', 239, 247),
     Span('LiC6', 282, 286)]

Each mention is returned as a Span, which contains the mention text, as well as the start and end character offsets within the containing document element.
