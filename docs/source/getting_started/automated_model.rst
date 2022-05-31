===========================================
BERT-based Automated Data Extraction Model
===========================================

BatteryDataExtractor can create a BERT-based automated data extraction model for materials property by just providing the list of names of properties::

    >>> from batterydataextractor.doc import Document
    >>> doc = Document("The theoretical capacity of graphite is 372 mAh/g... In the case of LiFePO4 chemistry, the absolute maximum voltage is 4.2V per cell.")
    >>> doc.add_models_by_names(["capacity", "voltage"])
    >>> records = doc.records
    >>> for r in records:
    >>>     print(r.serialize())
    {'PropertyData': {'value': [372.0], 'units': 'mAh / g', 'raw_value': '372 mAh / g', 'specifier': 'capacity', 'material': 'graphite', 'confidence_score': 0.6248}}
    {'PropertyData': {'value': [4.2], 'units': 'V', 'raw_value': '4.2 V', 'specifier': 'voltage', 'material': 'LiFePO4', 'confidence_score': 0.6432}}

Users can also extract non-battery-related properties and provide the confidence-score threshold. The original text can be saved by setting ``original_text`` as True::

    >>> text = 'The melting point (mp) of Aspirin (C9H8O4): 146-147 °C.'
    >>> doc = Document(text)
    >>> property_names = ["mp"]
    >>> doc.add_models_by_names(property_names, confidence_threshold=0.01, original_text=True)
    >>> for record in doc.records:
    >>>     print(record.serialize())
    {'PropertyData': {'value': [146.0, 147.0], 'units': '° C', 'raw_value': '146-147 ° C', 'specifier': 'mp', 'material': 'Aspirin', 'confidence_score': 0.3717, 'original_text': 'The melting point ( mp ) of Aspirin ( C9H8O4 ) : 146-147 ° C .'}}

Similarly, the model of data extraction of general information can be created by providing the name of the general infomation::

    >>> from batterydataextractor.doc.text import Paragraph
    >>> text = '1H NMR spectra were recorded on a Varian MR-400 MHz instrument.'
    >>> doc = Paragraph(text)
    >>> doc.add_general_models(["apparatus"], confidence_threshold=0.1, original_text=True)
    >>> for record in doc.records:
    >>>     print(record.serialize())
    {'GeneralInfo': {'answer': 'Varian MR - 400 MHz instrument', 'specifier': 'apparatus', 'confidence_score': 0.5065, 'original_text': '1H NMR spectra were recorded on a Varian MR - 400 MHz instrument .'}}

Or users can ask self-defined questions by setting ``self_defined`` as True::

    >>> from batterydataextractor.doc.text import Paragraph
    >>> text = 'For current LIBs based on OLE system, the employed cathodes could be mainly divided into two categories: LCO is still very popular in the consumer electronics market and Ni-rich compounds have already taken a place in the electric vehicles where the Tesla LiNi0.8Co0.15Al0.05O2 (NCA) cathode is a good example.'
    >>> doc = Paragraph(text)
    >>> doc.add_general_models(["Which cathode is commonly used in electric vehicles?"], confidence_threshold=0.1, self_defined=True)
    >>> for record in doc.records:
    >>>   print(record.serialize())
    {'GeneralInfo': {'answer': 'Ni - rich compounds', 'specifier': 'Which cathode is commonly used in electric vehicles?', 'confidence_score': 0.1489}}


