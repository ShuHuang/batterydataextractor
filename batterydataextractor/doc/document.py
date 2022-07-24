# -*- coding: utf-8 -*-
"""
batterydataextractor.doc.document

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Document model.
"""
from abc import ABCMeta, abstractmethod
import collections
import io
import json
import csv
import logging

import six

from .text import Paragraph, Citation, Footnote, Heading, Title, Caption
from .element import CaptionedElement
from .meta import MetaData
from ..errors import ReaderError
from ..model.base import ModelList
from ..model.model import PropertyData, Compound, GeneralInfo
from ..text import get_encoding
from ..config import Config


log = logging.getLogger(__name__)


class BaseDocument(six.with_metaclass(ABCMeta, collections.Sequence)):
    """Abstract base class for a Document."""

    def __repr__(self):
        return '<%s: %s elements>' % (self.__class__.__name__, len(self))

    def __str__(self):
        return '<%s: %s elements>' % (self.__class__.__name__, len(self))

    def __getitem__(self, index):
        return self.elements[index]

    def __len__(self):
        return len(self.elements)

    @property
    @abstractmethod
    def elements(self):
        """Return a list of document elements."""
        return []

    @property
    @abstractmethod
    def records(self):
        """Chemical records that have been parsed from this Document."""
        return []


class Document(BaseDocument):
    """A document to extract data from. Contains a list of document elements."""
    # TODO: Add a usage example here in the documentation.

    def __init__(self, *elements, **kwargs):
        """Initialize a Document manually by passing one or more Document elements (Paragraph, Heading, Table, etc.)
        Strings that are passed to this constructor are automatically wrapped into Paragraph elements.
        :param list[batterydataextractor.doc.element.BaseElement|string] elements: Elements in this Document.
        :keyword Config config: (Optional) Config file for the Document.
        :keyword list[BaseModel] models: (Optional) Models that the Document should extract data for.
        """
        self._elements = []
        for element in elements:
            # Convert raw text to Paragraph elements
            if isinstance(element, six.text_type):
                element = Paragraph(element)
            elif isinstance(element, six.binary_type):
                # Try guess encoding if byte string
                encoding = get_encoding(element)
                log.warning('Guessed bytestring encoding as %s. Use unicode strings to avoid this warning.', encoding)
                element = Paragraph(element.decode(encoding))
            element.document = self
            self._elements.append(element)
        if 'config' in kwargs.keys():
            self.config = kwargs['config']
        else:
            self.config = Config()
        if 'models' in kwargs.keys():
            self._models = kwargs['models']
        else:
            self._models = []

        if 'device' in kwargs.keys():
            self._device = kwargs['device']
        else:
            self._device = -1

        # Sets parameters from configuration file
        for element in elements:
            if callable(getattr(element, 'set_config', None)):
                element.set_config()
        log.debug('%s: Initializing with %s elements' % (self.__class__.__name__, len(self.elements)))

    def add_models(self, models):
        """
        Add models to all elements.
        Usage::
            d = Document.from_file(f)
            d.add_models([myModelClass1, myModelClass2,..])
        Arguments::
            models -- List of model classes
        """
        log.debug("Setting models")
        self._models.extend(models)
        for element in self.elements:
            if callable(getattr(element, 'add_models', None)):
                element.add_models(models)
        return

    def add_models_by_names(self, names, confidence_threshold=0, original_text=False):
        """
        Add models to all elements.
        Usage::
            d = Document.from_file(f)
            d.add_models_by_names("myModelName1", "myModelName2",..])
        Arguments::
            models -- List of model classes
        """
        log.debug("Setting models by names")

        model = PropertyData
        model.defined_names = names
        model.confidence_threshold = confidence_threshold
        model.original_text = original_text
        model.device = self.device
        self._models.extend([model])
        for element in self.elements:
            if callable(getattr(element, 'add_models', None)):
                element.add_models([model])
        return

    def add_general_models(self, names, confidence_threshold=0, original_text=False, self_defined=False):
        """
        Add models to all elements.
        Usage::
            d = Document.from_file(f)
            d.add_general_models("myModelName1", "myModelName2",..])
        Arguments::
            models -- List of model classes
        """
        log.debug("Setting models by names")

        model = GeneralInfo
        model.defined_names = names
        model.confidence_threshold = confidence_threshold
        model.original_text = original_text
        model.self_defined = self_defined
        model.device = self.device
        self._models.extend([model])
        for element in self.elements:
            if callable(getattr(element, 'add_models', None)):
                element.add_models([model])
        return

    @property
    def models(self):
        return self._models

    @models.setter
    def models(self, value):
        self._models = value
        for element in self.elements:
            element.models = value

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, value):
        self._device = value
        for element in self.elements:
            element.device = value

    @classmethod
    def from_file(cls, f, fname=None, readers=None):
        """Create a Document from a file.
        Usage::
            with open('paper.html', 'rb') as f:
                doc = Document.from_file(f)
        .. note::
            Always open files in binary mode by using the 'rb' parameter.
        :param f: A file-like object or path to a file.
        :type f: file or str
        :param str fname: (Optional) The filename. Used to help determine file format.
        :param list[batterydataextractor.reader.base.BaseReader] readers: (Optional) List of readers to use. If not set, Document will try all default readers,
            which are :class:`~batterydataextractor.reader.acs.AcsHtmlReader`, :class:`~batterydataextractor.reader.rsc.RscHtmlReader`,
            :class:`~batterydataextractor.reader.nlm.NlmXmlReader`, :class:`~batterydataextractor.reader.uspto.UsptoXmlReader`,
            :class:`~batterydataextractor.reader.cssp.CsspHtmlReader`, :class:`~batterydataextractor.elsevier.ElsevierXmlReader`,
            :class:`~batterydataextractor.reader.markup.XmlReader`, :class:`~batterydataextractor.reader.markup.HtmlReader`,
            :class:`~batterydataextractor.reader.pdf.PdfReader`, and :class:`~batterydataextractor.reader.plaintext.PlainTextReader`.
        """
        if isinstance(f, six.string_types):
            f = io.open(f, 'rb')
        if not fname and hasattr(f, 'name'):
            fname = f.name
        return cls.from_string(f.read(), fname=fname, readers=readers)

    @classmethod
    def from_string(cls, fstring, fname=None, readers=None):
        """Create a Document from a byte string containing the contents of a file.
        Usage::
            contents = open('paper.html', 'rb').read()
            doc = Document.from_string(contents)
        .. note::
            This method expects a byte string, not a unicode string (in contrast to most methods in batterydataextractor).
        :param bytes fstring: A byte string containing the contents of a file.
        :param str fname: (Optional) The filename. Used to help determine file format.
        :param list[batterydataextractor.reader.base.BaseReader] readers: (Optional) List of readers to use. If not set, Document will try all default readers,
            which are :class:`~batterydataextractor.reader.acs.AcsHtmlReader`, :class:`~batterydataextractor.reader.rsc.RscHtmlReader`,
            :class:`~batterydataextractor.reader.nlm.NlmXmlReader`, :class:`~batterydataextractor.reader.uspto.UsptoXmlReader`,
            :class:`~batterydataextractor.reader.cssp.CsspHtmlReader`, :class:`~batterydataextractor.elsevier.ElsevierXmlReader`,
            :class:`~batterydataextractor.reader.markup.XmlReader`, :class:`~batterydataextractor.reader.markup.HtmlReader`,
            :class:`~batterydataextractor.reader.pdf.PdfReader`, and :class:`~batterydataextractor.reader.plaintext.PlainTextReader`.
        """
        if readers is None:
            from ..reader import DEFAULT_READERS
            readers = DEFAULT_READERS

        if isinstance(fstring, six.text_type):
            raise ReaderError('from_string expects a byte string, not a unicode string')

        for reader in readers:
            # Skip reader if we don't think it can read file
            if not reader.detect(fstring, fname=fname):
                continue
            try:
                d = reader.readstring(fstring)
                log.debug('Parsed document with %s' % reader.__class__.__name__)
                return d
            except ReaderError:
                pass
        raise ReaderError('Unable to read document')

    @property
    def elements(self):
        """
        A list of all the elements in this document. All elements subclass from :class:`~batterydataextractor.doc.element.BaseElement`,
        and represent things such as paragraphs or tables, and can be found in :mod:`batterydataextractor.doc.figure`,
        :mod:`batterydataextractor.doc.table_new`, and :mod:`batterydataextractor.doc.text`.
        """
        return self._elements

#     # TODO: memoized_property? Why doc.records.serialize() parse many times?
    @property
    def records(self):
        """
        All records found in this Document, as a list of :class:`~batterydataextractor.model.base.BaseModel`.
        """
        log.debug("Getting chemical records")
        records = ModelList()  # Final list of records -- output
        head_def_record = None  # Most recent record from a heading, title or short paragraph
        head_def_record_i = None # Element index of head_def_record
        last_product_record = None
        title_record = None # Records found in the title

        # Main loop, over all elements in the document
        for i, el in enumerate(self.elements):
            log.debug("Element %d, type %s" %(i, str(type(el))))
            last_id_record = None

            # FORWARD INTERDEPENDENCY RESOLUTION -- Updated model parsers to reflect defined entities
            # 1. Find any defined entities in the element e.g. "Curie Temperature, Tc"
            # 2. Update the relevant models
            # TODO: recover definition
            # element_definitions = el.definitions
            # for model in el.models:
            #     model.update(element_definitions)

            el_records = el.records
            # Save the title compound
            if isinstance(el, Title):
                if len(el_records) == 1 and isinstance(el_records[0], Compound) and el_records[0].is_id_only:
                    title_record = el_records[0]

            # Reset head_def_record unless consecutive heading with no records
            if isinstance(el, Heading) and head_def_record is not None:
                if not (i == head_def_record_i + 1 and len(el.records) == 0):
                    head_def_record = None
                    head_def_record_i = None

            # Paragraph with single sentence with single ID record considered a head_def_record
            if isinstance(el, Paragraph) and len(el.sentences) == 1:
                if len(el_records) == 1 and isinstance(el_records[0], Compound) and el_records[0].is_id_only:
                    head_def_record = el_records[0]
                    head_def_record_i = i

            # Paragraph with multiple sentences
            # We assume that if the first sentence of a paragraph contains only 1 ID Record, we can treat it as a header definition record, unless directly proceeding a header def record
            elif isinstance(el, Paragraph) and len(el.sentences) > 0:
                if not (isinstance(self.elements[i - 1], Heading) and head_def_record_i == i - 1):
                    first_sent_records = el.sentences[0].records
                    if len(first_sent_records) == 1 and isinstance(first_sent_records[0], Compound) and first_sent_records[0].is_id_only:
                        sent_record = first_sent_records[0]
                        if sent_record.names:
                            head_def_record = sent_record
                            head_def_record_i = i

            #: BACKWARD INTERDEPENDENCY RESOLUTION BEGINS HERE
            for record in el_records:
                if isinstance(record, Compound):
                    # Keep track of the most recent compound record with labels
                    # Heading records with compound ID's
                    if isinstance(el, Heading) and record.names:
                        head_def_record = record
                        head_def_record_i = i
                        # If 2 consecutive headings with compound ID, merge in from previous
                        if i > 0 and isinstance(self.elements[i - 1], Heading):
                            prev = self.elements[i - 1]
                            if (len(el.records) == 1 and record.is_id_only and len(prev.records) == 1 and
                                isinstance(prev.records[0], Compound) and prev.records[0].is_id_only and
                                    not (record.names and prev.records[0].names)):
                                record.names.extend(prev.records[0].names)

                # Unidentified records -- those without compound names or labels
                if record.is_unidentified:
                    if hasattr(record, 'compound'):
                        # We have property values but no names or labels... try merge those from previous records
                        if isinstance(el, Paragraph) and (head_def_record or last_product_record or last_id_record or title_record):
                            # head_def_record from heading takes priority if the heading directly precedes the paragraph ( NOPE: or the last_id_record has no name)
                            if head_def_record_i and head_def_record_i + 1 == i: # or (last_id_record and not last_id_record.names)):
                                if head_def_record:
                                    record.compound = head_def_record
                                elif last_id_record:
                                    record.compound = last_id_record
                                elif last_product_record:
                                    record.compound = last_product_record
                                elif title_record:
                                    record.compound = title_record
                            else:
                                if last_id_record:
                                    record.compound = last_id_record
                                elif head_def_record:
                                    record.compound = head_def_record
                                elif last_product_record:
                                    record.compound = last_product_record
                                elif title_record:
                                    record.compound = title_record
                        else:
                            pass

                if record not in records:
                    log.debug(record.serialize())
                    records.append(record)

        # clean up records
        cleaned_records = ModelList()
        for record in records:
            if record.required_fulfilled and record not in cleaned_records:
                if (self.models and type(record) in self.models) or not self.models:
                    cleaned_records.append(record)

        # Reset updatables
        for el in self.elements:
            for model in el.models:
                model.reset_updatables()

        return cleaned_records

    def get_element_with_id(self, id):
        """
        Get element with the specified ID. If one is not found, None is returned.
        :param id: Identifier to search for.
        :returns: Element with specified ID
        :rtype: BaseElement or None
        """
        """Return the element with the specified ID."""
        # Should we maintain a hashmap of ids to make this more efficient? Probably overkill.
        # TODO: Elements can contain nested elements (captions, footnotes, table cells, etc.)
        return next((el for el in self.elements if el.id == id), None)

    @property
    def citations(self):
        """
        A list of all :class:`~batterydataextractor.doc.text.Citation` elements in this Document.
        """
        return [el for el in self.elements if isinstance(el, Citation)]

    @property
    def footnotes(self):
        """
        A list of all :class:`~batterydataextractor.doc.text.Footnote` elements in this Document.
        .. note::
            Elements (e.g. Tables) can contain nested Footnotes which are not taken into account.
        """
        # TODO: Elements (e.g. Tables) can contain nested Footnotes
        return [el for el in self.elements if isinstance(el, Footnote)]

    @property
    def titles(self):
        """
        A list of all :class:`~batterydataextractor.doc.text.Title` elements in this Document.
        """
        return [el for el in self.elements if isinstance(el, Title)]

    @property
    def headings(self):
        """
        A list of all :class:`~batterydataextractor.doc.text.Heading` elements in this Document.
        """
        return [el for el in self.elements if isinstance(el, Heading)]

    @property
    def paragraphs(self):
        """
        A list of all :class:`~batterydataextractor.doc.text.Paragraph` elements in this Document.
        """
        return [el for el in self.elements if isinstance(el, Paragraph)]

    @property
    def captions(self):
        """
        A list of all :class:`~batterydataextractor.doc.text.Caption` elements in this Document.
        """
        return [el for el in self.elements if isinstance(el, Caption)]

    @property
    def captioned_elements(self):
        """
        A list of all :class:`~batterydataextractor.doc.element.CaptionedElement` elements in this Document.
        """
        return [el for el in self.elements if isinstance(el, CaptionedElement)]

    @property
    def metadata(self):
        """Return metadata information
        """
        return [el for el in self.elements if isinstance(el, MetaData)]

    @property
    def abbreviation_definitions(self):
        """
        A list of all abbreviation definitions in this Document. Each abbreviation is in the form
        (:class:`str` abbreviation, :class:`str` long form of abbreviation, :class:`str` ner_tag)
        """
        return [ab for el in self.elements for ab in el.abbreviation_definitions]

    @property
    def ner_tags(self):
        """
        A list of all Named Entity Recognition tags in this Document.
        If a word was found not to be a named entity, the named entity tag is None,
        and if it was found to be a named entity, it can have either a tag of 'B-CM' for a beginning of a
        mention of a chemical or 'I-CM' for the continuation of a mention.
        """
        return [n for el in self.elements for n in el.ner_tags]

    @property
    def cems(self):
        """
        A list of all Chemical Entity Mentions in this document as :class:`~batterydataextractor.doc.text.Span`
        """
        return list(set([n for el in self.elements for n in el.cems]))

    def serialize(self):
        """
        Convert Document to Python dictionary. The dictionary will always contain the key 'type', which will be 'document',
        and the key 'elements', which contains a dictionary representation of each of the elements of the document.
        """
        # Serialize fields to a dict
        elements = []
        for element in self.elements:
            elements.append(element.serialize())
        data = {'type': 'document', 'elements': elements}
        return data

    def to_json(self, *args, **kwargs):
        """Convert Document to JSON string. The content of the JSON will be equivalent
        to that of :meth:`serialize`.
        The document itself will be under the key 'elements',
        and there will also be the key 'type', which will always be 'document'.
        Any arguments for :func:`json.dumps` can be passed into this function."""
        return json.dumps(self.serialize(), *args, **kwargs)

    def _repr_html_(self):
        html_lines = ['<div class="cde-document">']
        for element in self.elements:
            html_lines.append(element._repr_html_())
        html_lines.append('</div>')
        return '\n'.join(html_lines)

    def to_database(self, file_name, file_type='json'):
        """
        Save the document to a file in the database.

        :param file_name: The name of the file to save the document to.
        :param file_type: The type of file to save the document to.
        """
        if file_type == 'json':
            with open(file_name, 'a', encoding='utf-8') as f:
                json.dump(self.serialize(), f)
                f.write('\n')
        elif file_type == 'txt':
            with open(file_name, 'a', encoding='utf-8') as f:
                f.write(json.dumps(self.serialize()))
                f.write('\n')
        elif file_type == 'csv':
            data = self.serialize()
            dic = data[list(data.keys())[0]]
            dic['model_type'] = list(dic.keys())[0]
            csv_columns = dic.keys()
            with open(file_name, 'a', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                writer.writerow(dic)
        else:
            raise ValueError('Unknown file type. Please use json, txt, or csv.')
