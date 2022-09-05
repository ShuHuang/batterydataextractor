# BatteryDataExtractor
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://github.com/shuhuang/batterydataextractor/blob/master/LICENSE)

BatteryDataExtractor is a battery-aware text-mining software embedded with BERT models for automatically extracting chemical information from scientific literature. Full details available at [Documentation](https://batterydataextractor.readthedocs.io/en/latest/index.html).

## Features
   * Open-source battery-specific literature-mining toolkit
   * BERT-based token-classification models: abbreviation detection, part-of-speech tagging, chemical-named-entity recognition
   * Double-turn question-answering model for the data extraction of materials and properties
   * State-of-the-art performance on downstream evaluation data sets
   * Updated NLP plugins: new web scrapers, document readers, and tokenizers
   * New options: database auto-saving, original text-saving, and device-selection
   
## Installation 
Note: this command will be available after the paper has been accepted for publication:
```angular2html
pip install batterydataextractor
```

## Usage
### BERT-based Automated Model
#### Double-turn Q&A
```python
>>> from batterydataextractor.doc import Document
>>> doc = Document("The theoretical capacity of graphite is 372 mAh/g... In the case of LiFePO4 chemistry, the absolute maximum voltage is 4.2V per cell.")
>>> doc.add_models_by_names(["capacity", "voltage"])
>>> records = doc.records
>>> for r in records:
>>>    print(r.serialize())
{'PropertyData': {'value': [372.0], 'units': 'mAh / g', 'raw_value': '372 mAh / g', 'specifier': 'capacity', 'material': 'graphite', 'confidence_score': 0.6248}}
{'PropertyData': {'value': [4.2], 'units': 'V', 'raw_value': '4.2 V', 'specifier': 'voltage', 'material': 'LiFePO4', 'confidence_score': 0.6432}}
```

#### General Q&A
Provide the name of the general information:
```python
>>> from batterydataextractor.doc.text import Paragraph
>>> text = '1H NMR spectra were recorded on a Varian MR-400 MHz instrument.'
>>> doc = Paragraph(text)
>>> doc.add_general_models(["apparatus"], confidence_threshold=0.1, original_text=True)
>>> for record in doc.records:
>>>     print(record.serialize())
{'GeneralInfo': {'answer': 'Varian MR - 400 MHz instrument', 'specifier': 'apparatus', 'confidence_score': 0.5065, 'original_text': '1H NMR spectra were recorded on a Varian MR - 400 MHz instrument .'}}
}}
```
Ask self-defined questions:
```python
>>> from batterydataextractor.doc.text import Paragraph
>>> text = 'For current LIBs based on OLE system, the employed cathodes could be mainly divided into two categories: LCO is still very popular in the consumer electronics market and Ni-rich compounds have already taken a place in the electric vehicles where the Tesla LiNi0.8Co0.15Al0.05O2 (NCA) cathode is a good example.'
>>> doc = Paragraph(text)
>>> doc.add_general_models(["Which cathode is commonly used in electric vehicles?"], confidence_threshold=0.1, self_defined=True)
>>> for record in doc.records:
>>>   print(record.serialize())
{'GeneralInfo': {'answer': 'Ni - rich compounds', 'specifier': 'Which cathode is commonly used in electric vehicles?', 'confidence_score': 0.1489}}
```

### BERT-based NLP toolkit
Usage of new NLP toolkit can be found at [Documentation](https://batterydataextractor.readthedocs.io/en/latest/getting_started/natural_language_processing.html). BERT-based functionalities include part-of-speech (POS) tagging, abbreviation detection, and chemical named entity recognition.

## Citation

BatteryDataExtractor: battery-aware text-mining software embedded with BERT models
