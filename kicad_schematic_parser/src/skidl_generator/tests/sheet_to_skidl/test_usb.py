"""Tests for USB circuit conversion using real schematic."""
import os
import pytest
from skidl_generator.sheet_to_skidl import (
    parse_netlist_section,
    parse_component_section,
    sheet_to_skidl,
    Component,
    Net
)

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data")
with open(os.path.join(TEST_DIR, "usb_output.txt"), 'r') as f:
    USB_TEXT = f.read()

def test_usb_components():
    """Verify USB connector and supporting components are parsed correctly."""
    components = parse_component_section(USB_TEXT)
    
    # Should find 3 components (P1, C4, R1)
    assert len(components) == 3
    
    # Test USB connector
    p1 = next(c for c in components if c.reference == "P1")
    assert p1.library == "Connector"
    assert p1.part == "USB_C_Plug_USB2.0"
    assert p1.footprint == "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"

def test_usb_nets():
    """Verify USB power and data lines."""
    nets = parse_netlist_section(USB_TEXT)
    
    # Test main power nets
    assert "+5V" in nets
    assert "GND" in nets
    
    # Verify data lines
    assert "D+" in nets
    assert "D-" in nets
    assert "MERGED_NET_3" in nets  # CC pin connection

def test_usb_skidl_generation():
    """Verify generated SKiDL matches USB circuit requirements."""
    code = sheet_to_skidl("usb_interface", USB_TEXT)
    
    # Component validation
    assert "Part('Connector', 'USB_C_Plug_USB2.0')" in code
    assert "Part('Device', 'C', value='10uF')" in code
    assert "Part('Device', 'R', value='5.1K')" in code
    
    # Connection validation
    assert "p1['VBUS'] += +5V" in code
    assert "p1['D+'] += D+" in code
    assert "p1['D-'] += D-" in code
    assert "r1[1] += p1['CC']" in code
    assert "r1[2] += GND" in code
