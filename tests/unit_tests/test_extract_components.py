# -*- coding: utf-8 -*-

import sys
import os
import unittest

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from example_kicad_project_SKIDL.kicad_project_SKIDL.USB import USB
from src.skidl.tools.kicad8.extract_components import extract_subcircuit_components

class TestExtractComponents(unittest.TestCase):
    def test_usb_component_extraction(self):
        # Extract components from USB subcircuit
        components = extract_subcircuit_components(sys.modules[USB.__module__])
        
        # Verify we got the expected number of components
        self.assertEqual(len(components), 3, "Should extract exactly 3 components")
        
        # Find components by their tags
        components_by_tag = {comp.get('tag'): comp for comp in components}
        
        # Test capacitor C4
        c4 = components_by_tag.get('C4')
        self.assertIsNotNone(c4, "C4 component not found")
        self.assertEqual(c4['lib'], 'Device')
        self.assertEqual(c4['name'], 'C')
        self.assertEqual(c4['value'], '10uF')
        self.assertEqual(c4['footprint'], 'Capacitor_SMD:C_0603_1608Metric')
        self.assertEqual(c4['sheet_name'], 'USB')
        self.assertEqual(c4['sheet_file'], 'usb.kicad_sch')
        
        # Test USB connector P1
        p1 = components_by_tag.get('P1')
        self.assertIsNotNone(p1, "P1 component not found")
        self.assertEqual(p1['lib'], 'Connector')
        self.assertEqual(p1['name'], 'USB_C_Plug_USB2.0')
        self.assertEqual(p1['value'], 'USB_C_Plug_USB2.0')
        self.assertEqual(p1['footprint'], 'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
        self.assertEqual(p1['sheet_name'], 'USB')
        self.assertEqual(p1['sheet_file'], 'usb.kicad_sch')
        
        # Test resistor R1
        r1 = components_by_tag.get('R1')
        self.assertIsNotNone(r1, "R1 component not found")
        self.assertEqual(r1['lib'], 'Device')
        self.assertEqual(r1['name'], 'R')
        self.assertEqual(r1['value'], '5.1K')
        self.assertEqual(r1['footprint'], 'Resistor_SMD:R_0603_1608Metric')
        self.assertEqual(r1['sheet_name'], 'USB')
        self.assertEqual(r1['sheet_file'], 'usb.kicad_sch')

if __name__ == '__main__':
    unittest.main()
