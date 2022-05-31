=================================
Reading a Document
=================================

Most commonly, you want to pass an entire document file to BatteryDataExtractor. BatteryDataExtractor comes with three built-in Document readers that can read HTML or XML files. These readers are responsible for detecting different elements of a document and recompiling them into a single consistent document structure::

    >>> from batterydataextractor import Document
    >>> f = open('paper.html', 'rb')
    >>> doc = Document.from_file(f)

Each reader will be tried in turn until one is successfully able to read the file. If you know exactly which readers you want to use, it is possible to specify a list as an optional parameter::

    >>> f = open('rsc_article.html', 'rb')
    >>> doc = Document.from_file(f, readers=[RscHtmlReader()])

.. note:: Always open files in binary mode by using the 'rb' parameter.

Alternatively, you can load a document into BatteryDataExtractor by passing it some text::

    >>> doc = Document('The capacity of graphite is 372 mAh/g.')

At present, the available readers are:
    * RscHtmlReader - For RSC HTML articles
    * ElsevierXmlReader - For Elsevier XML papers
    * SpringerXmlReader - For Springer XML with JATS format
    * PlainTextReader - Generic plain text

.. rubric:: Document Elements

Once read, documents are represented by a single linear stream of `element` objects. This stream is now independent of the initial document type or the source::

    >>> doc.elements
    [Metadata('title, authors, journal, date, abstract...'),
    Heading('Abstract'),
    Paragraph('The first paragraph of text...'),
    ...]

Element types include Title, Heading, Paragraph, Citation, Table, Figure, Caption and Footnote. You can retrieve a specific element by its index within the document::

    >>> para = doc.elements[14]
    >>> para
    Paragraph(id=None, references=[], text='The mechanism of lithium intercalation in the so-called ‘soft’ anodes, i.e. graphite or graphitable carbons, is well known. It develops through well-identified, reversible stages, corresponding to progressive intercalation within discrete graphene layers, to reach the formation of LiC6 with a maximum theoretical capacity of 372 ± 2.4 mAh g−1.')

You can also get the individual sentences of a paragraph::

    >>> para.sentences
    [Sentence('The mechanism of lithium intercalation in the so-called ‘soft’ anodes, i.e. graphite or graphitable carbons, is well known.', 0, 123),
     Sentence('It develops through well-identified, reversible stages, corresponding to progressive intercalation within discrete graphene layers, to reach the formation of LiC6 with a maximum theoretical capacity of 372 ± 2.4 mAh g−1.', 124, 344)]

Or, the individual tokens::

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


as well as a list of individual chemical entity mentions (CEMs) of the document::

    >>> doc.cems
    [Span('5,10,15,20-Tetra(4-carboxyphenyl)porphyrin', 19, 61),
     Span('THF', 82, 85),
     Span('Tetrahydrofuran', 65, 80)]

Each mention is returned as a ``Span``, which contains the mention text, as well as the start and end character offsets within the containing document element.

You can also output the abbreviations found in the document::

    >>> doc.abbreviation_definitions
    [([u'THF'], [u'Tetrahydrofuran'], u'CM')]

