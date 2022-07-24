# -*- coding: utf-8 -*-
"""
batterydataextractor.doc.text

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Text-based document elements.
"""
from abc import abstractmethod, ABC
import collections
import logging
import re
import unicodedata
import six

from ..model.base import ModelList
from ..model.model import Compound
from ..nlp.lexicon import ChemLexicon, Lexicon
from ..nlp.cem import CemTagger
from ..nlp.abbrev import AbbreviationDetector
from ..nlp.tag import NoneTagger, BaseTagger, BertTagger
from ..nlp.tokenize import ChemSentenceTokenizer, ChemWordTokenizer, SentenceTokenizer, WordTokenizer
from ..utils import memoized_property
from .element import BaseElement
from ..text import CONTROL_RE


log = logging.getLogger(__name__)


class BaseText(BaseElement):
    """Abstract base class for a text Document Element."""

    def __init__(self, text, word_tokenizer=None, lexicon=None, abbreviation_detector=None, pos_tagger=None, ner_tagger=None, **kwargs):
        """
        .. note::
            If intended as part of a :class:`~batterydataextractor.doc.document.Document`,
            an element should either be initialized with a reference to its containing document,
            or its :attr:`document` attribute should be set as soon as possible.
            If the element is being passed in to a :class:`~batterydataextractor.doc.document.Document`
            to initialise it, the :attr:`document` attribute is automatically set
            during the initialisation of the document, so the user does not need to worry about this.
        :param str text: The text contained in this element.
        :param WordTokenizer word_tokenizer: (Optional) Word tokenizer for this element.
        :param Lexicon lexicon: (Optional) Lexicon for this element. The lexicon stores all the occurences of unique words and can provide
            Brown clusters for the words.
        :param AbbreviationDetector abbreviation_detector: (Optional) The abbreviation detector for this element.
        :param BaseTagger pos_tagger: (Optional) The part of speech tagger for this element.
        :param BaseTagger ner_tagger: (Optional) The named entity recognition tagger for this element.
        :param Document document: (Optional) The document containing this element.
        :param str label: (Optional) The label for the captioned element, e.g. Table 1 would have a label of 1.
        :param Any id: (Optional) Some identifier for this element. Must be equatable.
        :param list[batterydataextractor.models.BaseModel] models: (Optional) A list of models for this element to parse.
            If the element is part of another element (e.g. a :class:`~batterydataextractor.doc.text.Sentence`
            inside a :class:`~batterydataextractor.doc.text.Paragraph`), or is part of a :class:`~batterydataextractor.doc.document.Document`,
            this is set automatically to be the same as that of the containing element, unless manually set otherwise.
        """
        if not isinstance(text, six.text_type):
            raise TypeError('Text must be a unicode string')
        super(BaseText, self).__init__(**kwargs)
        self._text = unicodedata.normalize("NFKD", text)
        self.word_tokenizer = word_tokenizer if word_tokenizer is not None else self.word_tokenizer
        self.lexicon = lexicon if lexicon is not None else self.lexicon
        self.abbreviation_detector = abbreviation_detector if abbreviation_detector is not None else self.abbreviation_detector
        self.pos_tagger = pos_tagger if pos_tagger is not None else self.pos_tagger
        self.ner_tagger = ner_tagger if ner_tagger is not None else self.ner_tagger

    def __repr__(self):
        return '%s(id=%r, references=%r, text=%r)' % (self.__class__.__name__, self.id, self.references, self._text)

    def __str__(self):
        return self._text

    @property
    def text(self):
        """The raw text :class:`str` for this passage of text."""
        return self._text

    @property
    @abstractmethod
    def word_tokenizer(self):
        """The :class:`~batterydataextractor.nlp.tokenize.WordTokenizer` used by this element."""
        return

    @property
    @abstractmethod
    def lexicon(self):
        """The :class:`~batterydataextractor.nlp.lexicon.Lexicon` used by this element."""
        return

    @property
    @abstractmethod
    def pos_tagger(self):
        """The part of speech tagger used by this element. A subclass of :class:`~batterydataextractor.nlp.tag.BaseTagger`"""
        return

    @property
    @abstractmethod
    def ner_tagger(self):
        """The named entity recognition tagger used by this element. A subclass of :class:`~batterydataextractor.nlp.tag.BaseTagger`"""
        return

    @property
    @abstractmethod
    def tokens(self):
        """A list of :class:`Token` s for this object."""
        return

    @property
    @abstractmethod
    def tags(self):
        """
        A list of tags corresponding to each of the tokens in the object.
        For information on what each of the tags can be, check the documentation on
        the specific :attr:`ner_tagger` and :attr:`pos_tagger` used for this class.
        """
        return

    def serialize(self):
        """
        Convert self to a dictionary. The key 'type' will contain
        the name of the class being serialized, and the key 'content' will contain
        a serialized representation of :attr:`text`, which is a :class:`str`
        """
        data = {'type': self.__class__.__name__, 'content': self.text}
        return data

    def _repr_html_(self):
        return self.text

    @word_tokenizer.setter
    def word_tokenizer(self, value):
        self._word_tokenizer = value

    @lexicon.setter
    def lexicon(self, value):
        self._lexicon = value

    @pos_tagger.setter
    def pos_tagger(self, value):
        self._pos_tagger = value

    @ner_tagger.setter
    def ner_tagger(self, value):
        self._ner_tagger = value


class Text(collections.Sequence, BaseText):
    """A passage of text, comprising one or more sentences."""

    sentence_tokenizer = ChemSentenceTokenizer()
    word_tokenizer = ChemWordTokenizer()
    lexicon = ChemLexicon()
    abbreviation_detector = AbbreviationDetector()
    pos_tagger = BertTagger()
    ner_tagger = CemTagger()

    def __init__(self, text, sentence_tokenizer=None, word_tokenizer=None, lexicon=None, abbreviation_detector=None, pos_tagger=None, ner_tagger=None, parsers=None, **kwargs):
        """
        .. note::
            If intended as part of a :class:`~batterydataextractor.doc.document.Document`,
            an element should either be initialized with a reference to its containing document,
            or its :attr:`document` attribute should be set as soon as possible.
            If the element is being passed in to a :class:`~batterydataextractor.doc.document.Document`
            to initialise it, the :attr:`document` attribute is automatically set
            during the initialisation of the document, so the user does not need to worry about this.
        :param str text: The text contained in this element.
        :param SentenceTokenizer sentence_tokenizer: (Optional) Sentence tokenizer for this element.
            Default :class:`~batterydataextractor.nlp.tokenize.ChemSentenceTokenizer`.
        :param WordTokenizer word_tokenizer: (Optional) Word tokenizer for this element.
            Default :class:`~batterydataextractor.nlp.tokenize.ChemWordTokenizer`.
        :param Lexicon lexicon: (Optional) Lexicon for this element. The lexicon stores all the occurences of unique words and can provide
            Brown clusters for the words. Default :class:`~batterydataextractor.nlp.lexicon.ChemLexicon`
        :param AbbreviationDetector abbreviation_detector: (Optional) The abbreviation detector for this element.
            Default :class:`~batterydataextractor.nlp.abbrev.ChemAbbreviationDetector`.
        :param BaseTagger pos_tagger: (Optional) The part of speech tagger for this element.
            Default :class:`~batterydataextractor.nlp.pos.ChemCrfPosTagger`.
        :param BaseTagger ner_tagger: (Optional) The named entity recognition tagger for this element.
            Default :class:`~batterydataextractor.nlp.cem.CemTagger`
        :param Document document: (Optional) The document containing this element.
        :param str label: (Optional) The label for the captioned element, e.g. Table 1 would have a label of 1.
        :param Any id: (Optional) Some identifier for this element. Must be equatable.
        :param list[batterydataextractor.models.BaseModel] models: (Optional) A list of models for this element to parse.
            If the element is part of another element (e.g. a :class:`~batterydataextractor.doc.text.Sentence`
            inside a :class:`~batterydataextractor.doc.text.Paragraph`), or is part of a :class:`~batterydataextractor.doc.document.Document`,
            this is set automatically to be the same as that of the containing element, unless manually set otherwise.
        """
        super(Text, self).__init__(text, word_tokenizer=word_tokenizer, lexicon=lexicon,
                                   abbreviation_detector=abbreviation_detector, pos_tagger=pos_tagger,
                                   ner_tagger=ner_tagger, parsers=None, **kwargs)
        self.sentence_tokenizer = sentence_tokenizer if sentence_tokenizer is not None else self.sentence_tokenizer
        self.pos_tagger.device = self.device
        self.ner_tagger.device = self.device

    def __getitem__(self, index):
        return self.sentences[index]

    def __len__(self):
        return len(self.sentences)

    def set_config(self):
        """ Load settings from configuration file
        .. note:: Called when Document instance is created
        """

        if self.document is None:
            pass
        else:
            c = self.document.config
            if 'SENTENCE_TOKENIZER' in c.keys():
                self.sentence_tokenizer = eval(c['SENTENCE_TOKENIZER'])()
            if 'WORD_TOKENIZER' in c.keys():
                self.word_tokenizer = eval(c['WORD_TOKENIZER'])()
            if 'POS_TAGGER' in c.keys():
                self.pos_tagger = eval(c['POS_TAGGER'])()
            if 'NER_TAGGER' in c.keys():
                self.ner_tagger = eval(c['NER_TAGGER'])()
            if 'LEXICON' in c.keys():
                self.lexicon = eval(c['LEXICON'])()
            if 'PARSERS' in c.keys():
                raise(DeprecationWarning('Manually setting parsers deprecated, any settings from config files for this will be ignored.'))

    @memoized_property
    def sentences(self):
        """A list of :class:`Sentence` s that make up this text passage."""
        sents = []
        spans = self.sentence_tokenizer.span_tokenize(self.text)
        for span in spans:
            sent = Sentence(
                text=self.text[span[0]:span[1]],
                start=span[0],
                end=span[1],
                word_tokenizer=self.word_tokenizer,
                lexicon=self.lexicon,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
                document=self.document,
                models=self.models,
                device=self.device
            )
            sents.append(sent)
        return sents

    @property
    def raw_sentences(self):
        """A list of :class:`str` for the sentences that make up this text passage."""
        return [sentence.text for sentence in self.sentences]

    @property
    def tokens(self):
        return [sent.tokens for sent in self.sentences]

    @property
    def raw_tokens(self):
        """A list of :class:`str` representations for the tokens of each sentence in this text passage."""
        return [sent.raw_tokens for sent in self.sentences]

    @property
    def pos_tagged_tokens(self):
        """A list of (:class:`Token` token, :class:`str` tag) tuples for each sentence in this text passage."""
        return [sent.pos_tagged_tokens for sent in self.sentences]

    @property
    def pos_tags(self):
        """A list of :class:`str` part of speech tags for each sentence in this text passage."""
        return [sent.pos_tags for sent in self.sentences]

    @memoized_property
    def unprocessed_ner_tagged_tokens(self):
        """
        A list of (:class:`Token` token, :class:`str` named entity recognition tag)
        from the text.
        No corrections from abbreviation detection are performed.
        """
        return [sent.unprocessed_ner_tagged_tokens for sent in self.sentences]

    @memoized_property
    def unprocessed_ner_tags(self):
        """
        A list of :class:`str` unprocessed named entity tags for the tokens in this sentence.
        No corrections from abbreviation detection are performed.
        """
        return [sent.unprocessed_ner_tags for sent in self.sentences]

    @property
    def ner_tagged_tokens(self):
        """
        A list of (:class:`Token` token, :class:`str` named entity recognition tag)
        from the text.
        """
        return [sent.ner_tagged_tokens for sent in self.sentences]

    @property
    def ner_tags(self):
        """
        A list of named entity tags corresponding to each of the tokens in the object.
        For information on what each of the tags can be, check the documentation on
        the specific :attr:`ner_tagger` used for this object.
        """
        return [sent.ner_tags for sent in self.sentences]

    @property
    def cems(self):
        """
        A list of all Chemical Entity Mentions in this text as :class:`batterydataextractor.doc.text.span`
        """
        return [cem for sent in self.sentences for cem in sent.cems]

    @property
    def tagged_tokens(self):
        """
        A list of (:class:`Token` token, :class:`str` named entity recognition tag)
        from the text.
        """
        return [sent.tagged_tokens for sent in self.sentences]

    @property
    def tags(self):
        return [sent.tags for sent in self.sentences]

    @property
    def abbreviation_definitions(self):
        """
        A list of all abbreviation definitions in this Document. Each abbreviation is in the form
        (:class:`str` abbreviation, :class:`str` long form of abbreviation, :class:`str` ner_tag)
        """
        return [ab for sent in self.sentences for ab in sent.abbreviation_definitions if ab != []]

    @property
    def records(self):
        """All records found in the object, as a list of :class:`~batterydataextractor.model.base.BaseModel`."""
        return ModelList(*[r for sent in self.sentences for r in sent.records])

    def __add__(self, other):
        if type(self) == type(other):
            merged = self.__class__(
                text=self.text + other.text,
                id=self.id or other.id,
                references=self.references + other.references,
                sentence_tokenizer=self.sentence_tokenizer,
                word_tokenizer=self.word_tokenizer,
                lexicon=self.lexicon,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
            )
            return merged
        return NotImplemented


class Title(Text, ABC):

    def __init__(self, text, **kwargs):
        super(Title, self).__init__(text, **kwargs)
        self.models = [Compound]

    def _repr_html_(self):
        return '<h1 class="bde-title">' + self.text + '</h1>'


class Heading(Text):

    def __init__(self, text, **kwargs):
        super(Heading, self).__init__(text, **kwargs)
        self.models = [Compound]

    def _repr_html_(self):
        return '<h2 class="bde-title">' + self.text + '</h2>'


class Paragraph(Text):

    def __init__(self, text, **kwargs):
        super(Paragraph, self).__init__(text, **kwargs)
        self.models = [Compound]

    def _repr_html_(self):
        return '<p class="bde-paragraph">' + self.text + '</p>'


class Footnote(Text):

    def __init__(self, text, **kwargs):
        super(Footnote, self).__init__(text, **kwargs)

    def _repr_html_(self):
        return '<p class="bde-footnote">' + self.text + '</p>'


class Citation(Text):
    ner_tagger = NoneTagger()  #: No tagging is done for citations
    abbreviation_detector = None

    def _repr_html_(self):
        return '<p class="bde-citation">' + self.text + '</p>'


class Caption(Text):

    def __init__(self, text, **kwargs):
        super(Caption, self).__init__(text, **kwargs)
        self.models = [Compound]

    def _repr_html_(self):
        return '<caption class="bde-caption">' + self.text + '</caption>'


class Abstract(Text):
    def __init__(self, text, **kwargs):
        super(Abstract, self).__init__(text, **kwargs)
        self.models = [Compound]

    def _repr_html_(self):
        return '<h2 class="bde-abstract">' + self.text + '</h2>'


class Sentence(BaseText, ABC):
    """A single sentence within a text passage."""

    word_tokenizer = ChemWordTokenizer()
    lexicon = ChemLexicon()
    abbreviation_detector = AbbreviationDetector()
    pos_tagger = BertTagger()
    ner_tagger = CemTagger()

    def __init__(self, text, start=0, end=None, word_tokenizer=None, lexicon=None, abbreviation_detector=None, pos_tagger=None, ner_tagger=None, **kwargs):
        """
        .. note::
            If intended as part of a :class:`batterydataextractor.doc.document.Document`,
            an element should either be initialized with a reference to its containing document,
            or its :attr:`document` attribute should be set as soon as possible.
            If the element is being passed in to a :class:`batterydataextractor.doc.document.Document`
            to initialise it, the :attr:`document` attribute is automatically set
            during the initialisation of the document, so the user does not need to worry about this.
        :param str text: The text contained in this element.
        :param int start: (Optional) The starting index of the sentence within the containing element. Default 0.
        :param int end: (Optional) The end index of the sentence within the containing element. Defualt None
        :param WordTokenizer word_tokenizer: (Optional) Word tokenizer for this element.
            Default :class:`~batterydataextractor.nlp.tokenize.ChemWordTokenizer`.
        :param Lexicon lexicon: (Optional) Lexicon for this element. The lexicon stores all the occurences of unique words and can provide
            Brown clusters for the words. Default :class:`~batterydataextractor.nlp.lexicon.ChemLexicon`
        :param AbbreviationDetector abbreviation_detector: (Optional) The abbreviation detector for this element.
            Default :class:`~batterydataextractor.nlp.abbrev.AbbreviationDetector`.
        :param BaseTagger pos_tagger: (Optional) The part of speech tagger for this element.
            Default :class:`~batterydataextractor.nlp.pos.ChemCrfPosTagger`.
        :param BaseTagger ner_tagger: (Optional) The named entity recognition tagger for this element.
            Default :class:`~batterydataextractor.nlp.cem.CemTagger`
        :param Document document: (Optional) The document containing this element.
        :param str label: (Optional) The label for the captioned element, e.g. Table 1 would have a label of 1.
        :param Any id: (Optional) Some identifier for this element. Must be equatable.
        :param list[batterydataextractor.models.BaseModel] models: (Optional) A list of models for this element to parse.
            If the element is part of another element (e.g. a :class:`~batterydataextractor.doc.text.Sentence`
            inside a :class:`~batterydataextractor.doc.text.Paragraph`), or is part of a :class:`~batterydataextractor.doc.document.Document`,
            this is set automatically to be the same as that of the containing element, unless manually set otherwise.
        """
        self.models = [Compound]
        super(Sentence, self).__init__(text, word_tokenizer=word_tokenizer, lexicon=lexicon, abbreviation_detector=abbreviation_detector, pos_tagger=pos_tagger, ner_tagger=ner_tagger, **kwargs)
        #: The start index of this sentence within the text passage.
        self.start = start
        #: The end index of this sentence within the text passage.
        self.end = end if end is not None else len(text)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self._text, self.start, self.end)

    @memoized_property
    def tokens(self):
        spans = self.word_tokenizer.span_tokenize(self.text)
        toks = [Token(
            text=self.text[span[0]:span[1]],
            start=span[0] + self.start,
            end=span[1] + self.start,
            lexicon=self.lexicon
        ) for span in spans]
        return toks

    @property
    def raw_tokens(self):
        """A list of :class:`str` representations for the tokens in the object."""
        return [token.text for token in self.tokens]

    @memoized_property
    def pos_tagged_tokens(self):
        """A list of (:class:`Token` token, :class:`str` tag) tuples for each sentence in this sentence."""
        # log.debug('Getting pos tags')
        return self.pos_tagger.tag(self.raw_tokens)

    @property
    def pos_tags(self):
        """A list of :class:`str` part of speech tags for each sentence in this sentence."""
        return [tag for token, tag in self.pos_tagged_tokens]

    @memoized_property
    def unprocessed_ner_tagged_tokens(self):
        """
        A list of (:class:`Token` token, :class:`str` named entity recognition tag)
        from the text.
        No corrections from abbreviation detection are performed.
        """
        return self.ner_tagger.tag(self.pos_tagged_tokens)

    @memoized_property
    def unprocessed_ner_tags(self):
        """
        A list of :class:`str` unprocessed named entity tags for the tokens in this sentence.
        No corrections from abbreviation detection are performed.
        """
        return [tag for token, tag in self.unprocessed_ner_tagged_tokens]

    @memoized_property
    def abbreviation_definitions(self):
        """
        A list of all abbreviation definitions in this Document. Each abbreviation is in the form
        (:class:`str` abbreviation, :class:`str` long form of abbreviation, :class:`str` ner_tag)
        """
        abbreviations, long_words = [], []
        if self.abbreviation_detector:
            log.debug('Detecting abbreviations')
            abbr_spans, long_spans = self.abbreviation_detector.detect_spans(self.raw_tokens)
            if abbr_spans:
                for abbr_span in abbr_spans:
                    abb = " ".join(self.raw_tokens)[abbr_span[0]:abbr_span[1]]
                    abbr = ("Abbr: ", abb)
                    abbreviations.append(abbr)
            if long_spans:
                for long_span in long_spans:
                    lon = " ".join(self.raw_tokens)[long_span[0]:long_span[1]]
                    long = ("LF: ", lon)
                    long_words.append(long)
        return abbreviations, long_words

    @memoized_property
    def ner_tagged_tokens(self):
        """
        A list of (:class:`Token` token, :class:`str` named entity recognition tag)
        from the sentence.
        """
        return list(zip(self.raw_tokens, self.ner_tags))

    @memoized_property
    def ner_tags(self):
        """
        A list of named entity tags corresponding to each of the tokens in the object.
        For information on what each of the tags can be, check the documentation on
        the specific :attr:`ner_tagger` used for this object.
        """
        # log.debug('Getting ner_tags')
        ner_tags = self.unprocessed_ner_tags
        return ner_tags

    @memoized_property
    def cems(self):
        """
        A list of all Chemical Entity Mentions in this text as :class:`~batterydataextractor.doc.text.Span`
        """
        log.debug('Getting cems')
        spans = []
        raw_tokens = self.raw_tokens
        for index, result in enumerate(self.ner_tags):
            if result == 'MAT':
                ner_word = raw_tokens[index].replace("(", "\\(").replace(")", "\\)")
                span = Span(text=raw_tokens[index], start=re.search(ner_word, self.text).start() + self.start,
                            end=re.search(ner_word, self.text).end() + self.start)
                spans.append(span)
        return spans

    @memoized_property
    def tags(self):
        tags = self.pos_tags
        for i, tag in enumerate(self.ner_tags):
            if tag is not None:
                tags[i] = tag
        return tags

    @property
    def tagged_tokens(self):
        """
        A list of (:class:`Token` token, :class:`str` named entity recognition tag)
        from the text.
        """
        return list(zip(self.raw_tokens, self.tags))

    @property
    def records(self):
        """All records found in the object, as a list of :class:`~batterydataextractor.model.base.BaseModel`."""
        records = ModelList()
        # Ensure no control characters are sent to a parser (need to be XML compatible)
        tagged_tokens = [(CONTROL_RE.sub('', token), tag) for token, tag in self.tagged_tokens]
        for model in self._streamlined_models:
            for parser in model.parsers:
                if hasattr(parser, 'parse_sentence'):
                    for record in parser.parse_sentence(tagged_tokens):
                        p = record.serialize()
                        if not p:  # TODO: Potential performance issues?
                            continue
                        # Skip duplicate records
                        if record in records:
                            continue
                        records.append(record)
        # i = 0
        # length = len(records)
        # while i < length:
        #     j = 0
        #     while j < length:
        #         if i != j:
        #             records[j].merge_all(records[i])
        #         j += 1
        #     i += 1
        return records

    def __add__(self, other):
        if type(self) == type(other):
            merged = self.__class__(
                text=self.text + other.text,
                start=self.start,
                end=None,
                id=self.id or other.id,
                references=self.references + other.references,
                word_tokenizer=self.word_tokenizer,
                lexicon=self.lexicon,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
            )
            return merged
        return NotImplemented


class Span(object):
    """A text span within a sentence."""

    def __init__(self, text, start, end):
        """
        :param str text: The text contained by this span.
        :param int start: The start offset of this token in the original text.
        :param int end: The end offsent of this token in the original text.
        """
        self.text = text
        """The :class:`str` text content of this span."""
        self.start = start
        """The :class:`int` start offset of this token in the original text."""
        self.end = end
        """The :class:`int` end offset of this token in the original text."""

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.text, self.start, self.end)

    def __str__(self):
        return self.text

    def __eq__(self, other):
        """Span objects are equal if the source text is equal, and the start and end indices are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.text == other.text and self.start == other.start and self.end == other.end

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.text, self.start, self.end))

    @property
    def length(self):
        """The :class:`int` offset length of this span in the original text."""
        return self.end - self.start


class Token(Span):
    """A single token within a sentence. Corresponds to a word, character, punctuation etc."""

    def __init__(self, text, start, end, lexicon):
        """
        :param str text: The text contained by this token.
        :param int start: The start offset of this token in the original text.
        :param int end: The end offsent of this token in the original text.
        :param Lexicon lexicon: The lexicon which contains this token.
        """
        super(Token, self).__init__(text, start, end)
        #: The lexicon for this token.
        self.lexicon = lexicon
        self.lexicon.add(text)

    @property
    def lex(self):
        """The corresponding :class:`batterydataextractor.nlp.lexicon.Lexeme` entry in the Lexicon for this token."""
        return self.lexicon[self.text]
