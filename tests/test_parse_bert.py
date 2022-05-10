import logging
import unittest
from batterydataextractor.doc import Document

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TestPropertyDataMp(unittest.TestCase):

    def do_parse(self, input, expected):
        p = Document(input)
        p.add_models_by_names(["mp"])
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_mpc1(self):
        s = 'NaCl: mp 163-164 °C.'
        expected = [{'PropertyData': {'confidence_score': 0.608,
                                      'material': 'NaCl',
                                      'raw_value': '163-164 ° C',
                                      'specifier': 'mp',
                                      'units': '° C',
                                      'value': [163.0, 164.0]}}]
        self.do_parse(s, expected)

    def test_mpc2(self):
        s = 'Bromo-2,6-dichloroaniline: mp 71-72° C.'
        expected = [{'PropertyData': {'confidence_score': 0.9909,
                                      'material': 'Bromo-2,6-dichloroaniline',
                                      'raw_value': '71-72 ° C',
                                      'specifier': 'mp',
                                      'units': '° C',
                                      'value': [71.0, 72.0]}}]
        self.do_parse(s, expected)


class TestOriginalText(unittest.TestCase):

    def do_parse(self, input, expected):
        p = Document(input)
        p.add_models_by_names(["capacity", "voltage"], original_text=True)
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_original_test(self):
        s = "The theoretical capacity of graphite is 372 mAh/g... In the case of LiFePO4 chemistry, the absolute " \
            "maximum voltage is 4.2V per cell."
        expected = [{'PropertyData': {'confidence_score': 0.6054, 'material': 'graphite',
                                      'original_text': 'The theoretical capacity of graphite is 372 mAh / g ... In the '
                                                       'case of LiFePO4 chemistry , the absolute maximum voltage is '
                                                       '4.2 V per cell .',
                                      'raw_value': '372 mAh / g', 'specifier': 'capacity', 'units': 'mAh / g',
                                      'value': [372.0]}},
                    {'PropertyData': {'confidence_score': 0.7035, 'material': 'LiFePO4',
                                      'original_text': 'The theoretical capacity of graphite is 372 mAh / g ... '
                                                       'In the case of LiFePO4 chemistry , the absolute maximum '
                                                       'voltage is 4.2 V per cell .',
                                      'raw_value': '4.2 V', 'specifier': 'voltage', 'units': 'V', 'value': [4.2]}}]
        self.do_parse(s, expected)


class TestGeneralInfoApparatus(unittest.TestCase):

    def do_parse(self, input, expected):
        p = Document(input)
        p.add_general_models(["apparatus"])
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_appra1(self):
        s = '1H NMR spectra were recorded on a Varian MR-400 MHz instrument.'
        expected = [{'GeneralInfo':
                         {'answer': 'Varian MR - 400 MHz instrument',
                          'confidence_score': 0.5065,
                          'specifier': 'apparatus'}}]
        self.do_parse(s, expected)

    def test_appra2(self):
        s = 'The photoluminescence quantum yield (PLQY) was measured using a FluoroMax-4 spectrofluorimeter.'
        expected = [{'GeneralInfo':
                                {'answer': 'FluoroMax-4 spectrofluorimeter',
                                 'confidence_score': 0.8481,
                                 'specifier': 'apparatus'}}]
        self.do_parse(s, expected)


class TestGeneralInfoElectrolyte(unittest.TestCase):

    def do_parse(self, input, expected):
        p = Document(input)
        p.add_general_models(["electrolyte"])
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_electrolyte(self):
        s = 'The typical non-aqueous electrolyte for commercial Li-ion cells is a solution of LiPF6 in linear and ' \
            'cyclic carbonates such as dimethyl carbonate and ethylene carbonate, respectively [1], [2].'
        expected = [{'GeneralInfo': {'answer': 'a solution of LiPF6', 'confidence_score': 0.3122,
                                     'specifier': 'electrolyte'}}]
        self.do_parse(s, expected)


class TestGeneralInfoDeviceComponent(unittest.TestCase):

    def do_parse(self, input, expected):
        p = Document(input)
        p.add_general_models(["anode", "cathode"])
        log.debug(p)
        log.debug([r.serialize() for r in p.records])
        self.assertEqual(expected, [r.serialize() for r in p.records])

    def test_device_component(self):
        s = 'The lithium iron phosphate battery (LiFePO4 battery) or LFP battery (lithium ferrophosphate), is a type ' \
            'of lithium-ion battery using lithium iron phosphate (LiFePO4) as the cathode material, and a graphitic ' \
            'carbon electrode with a metallic backing as the anode.'
        expected = [{'GeneralInfo': {'answer': 'graphitic carbon', 'confidence_score': 0.7898, 'specifier': 'anode'}},
                    {'GeneralInfo': {'answer': 'lithium iron phosphate', 'confidence_score': 0.9312,
                                     'specifier': 'cathode'}}]
        self.do_parse(s, expected)


if __name__ == '__main__':
    unittest.main()
