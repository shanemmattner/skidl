"""Tests for power regulator circuit conversion using real schematic."""
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
with open(os.path.join(TEST_DIR, "power2_output.txt"), 'r') as f:
    POWER2_TEXT = f.read()

def test_power_components():
    """Verify voltage regulator and supporting components are parsed correctly."""
    components = parse_component_section(POWER2_TEXT)
    
    # Should find 9 components (U1, R2, R7, R8, R11, C2, C3, C9, C11)
    assert len(components) == 9
    
    # Test voltage regulator
    u1 = next(c for c in components if c.reference == "U1")
    assert u1.library == "Regulator_Linear"
    assert u1.part == "NCP1117-3.3_SOT223"
    assert u1.footprint == "Package_TO_SOT_SMD:SOT-223-3_TabPin2"

def test_power_nets():
    """Verify power distribution networks and monitoring circuits."""
    nets = parse_netlist_section(POWER2_TEXT)
    
    # Test main power nets
    assert "+3V3" in nets
    assert "+5V" in nets
    assert "GND" in nets
    
    # Verify monitoring circuits
    assert "3v3_monitor" in nets
    assert "5v_monitor" in nets

def test_power_skidl_generation():
    """Verify generated SKiDL matches power circuit requirements."""
    code = sheet_to_skidl("power_regulator", POWER2_TEXT)
    print(f'Generated code:\n{code}')
    
    # Component validation
    assert "Part('Regulator_Linear', 'NCP1117-3.3_SOT223', value='NCP1117-3.3_SOT223')" in code
    assert "Part('Device', 'C', value='10uF')" in code
    assert "Part('Device', 'R', value='R')" in code  # Multiple resistors
    
    # Connection validation
    assert "u1['VI'] += +5V" in code
    assert "u1['VO'] += +3V3" in code
    assert "c2[1] += +3V3" in code
    assert "c3[2] += GND" in code
    assert "r11[1] += 3v3_monitor" in code
