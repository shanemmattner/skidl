"""Tests for the sheet to SKiDL converter using real schematic examples."""
import os
import pytest
from skidl_generator.sheet_to_skidl import (
    parse_netlist_section,
    parse_component_section,
    sheet_to_skidl,
    Component,
    Net
)

# Get test data directory
TEST_DIR = os.path.join(os.path.dirname(__file__), "test_data")

# Read sample data using relative path
with open(os.path.join(TEST_DIR, "resistor_divider_output.txt"), 'r') as f:
    RESISTOR_DIVIDER_TEXT = f.read()

# Similarly for the hierarchy file:
# with open(os.path.join(TEST_DIR, "hierarchy.txt"), 'r') as f:
#     HIERARCHY_TEXT = f.read()

def test_parse_netlist_section_real():
    """Test parsing netlist section from real resistor divider example."""
    nets = parse_netlist_section(RESISTOR_DIVIDER_TEXT)
    
    # Test GND net
    assert "GND" in nets
    assert nets["GND"].type == "power"
    assert "#PWR028 Pin 1 (~)" not in nets["GND"].pins  # Should skip power pins
    assert "C10.2" in nets["GND"].pins
    assert "R10.2" in nets["GND"].pins
    
    # Test VOUT net
    assert "VOUT" in nets
    assert nets["VOUT"].type == "hierarchical"
    assert len(nets["VOUT"].pins) == 3
    assert "R10.1" in nets["VOUT"].pins
    assert "R9.2" in nets["VOUT"].pins
    assert "C10.1" in nets["VOUT"].pins
    
    # Test VIN net
    assert "VIN" in nets
    assert nets["VIN"].type == "hierarchical"
    assert nets["VIN"].pins == ["R9.1"]

def test_parse_component_section_real():
    """Test parsing component section from real resistor divider example."""
    components = parse_component_section(RESISTOR_DIVIDER_TEXT)
    
    # Should find 3 components
    assert len(components) == 3
    
    # Check R9 properties
    r9 = next(c for c in components if c.reference == "R9")
    assert r9.library == "Device"
    assert r9.part == "R"
    assert r9.value == "2k"
    assert r9.footprint == "Resistor_SMD:R_0603_1608Metric"
    
    # Check R10 properties
    r10 = next(c for c in components if c.reference == "R10")
    assert r10.library == "Device"
    assert r10.part == "R"  
    assert r10.value == "1k"
    assert r10.footprint == "Resistor_SMD:R_0603_1608Metric"
    
    # Check C10 properties
    c10 = next(c for c in components if c.reference == "C10")
    assert c10.library == "Device"
    assert c10.part == "C"
    assert c10.value == "100nF"

def test_resistor_divider_skidl_generation():
    """Test generating SKiDL code from real resistor divider example."""
    expected_code = """@subcircuit
def resistor_divider(vin, vout):
    # Create components
    r9 = Part('Device', 'R', value='2k')
    r10 = Part('Device', 'R', value='1k')
    c10 = Part('Device', 'C', value='100nF')

    # Connect nets
    r9[1] += vin
    r10[1] += vout, r9[2], c10[1]
    r10[2] += GND, c10[2]"""

    code = sheet_to_skidl("resistor_divider", RESISTOR_DIVIDER_TEXT)
    
    # Normalize whitespace for comparison
    code = "\n".join(line.rstrip() for line in code.split("\n"))
    expected = "\n".join(line.rstrip() for line in expected_code.split("\n"))
    
    assert code == expected

# def test_parse_3v3_regulator():
#     """Test parsing the 3.3V regulator sheet from hierarchy.txt."""
#     # Find the section about power2.kicad_sch in hierarchy.txt
#     section_start = "analyzing: example_kicad_project/power2.kicad_sch"
#     section_end = "=== Sub-sheets found ==="

#     with open('src/skidl_generator/tests/conversion_test/test_data/hierarchy.txt', 'r') as f:
#         text = f.read()

#     start_idx = text.find(section_start)
#     end_idx = text.find(section_end, start_idx)
#     regulator_text = text[start_idx:end_idx]

#     # Generate SKiDL code for the regulator
#     code = sheet_to_skidl("regulator_3v3", regulator_text)

#     # Expected connections:
#     # - U1: NCP1117-3.3 regulator with input, output, and GND
#     # - C2, C3: Input/output filter caps
#     # - R8, R11, C11: Output voltage monitoring divider
#     # - R2, R7, C9: Input voltage monitoring divider
#     expected_parts = [
#         "u1 = Part('Regulator_Linear', 'NCP1117-3.3_SOT223'",
#         "c2 = Part('Device', 'C', value='10uF'",
#         "c3 = Part('Device', 'C', value='10uF'",
#         "c9 = Part('Device', 'C'",
#         "c11 = Part('Device', 'C'",
#         "r2 = Part('Device', 'R'",
#         "r7 = Part('Device', 'R'",
#         "r8 = Part('Device', 'R'",
#         "r11 = Part('Device', 'R'"
#     ]

#     for part in expected_parts:
#         assert part in code, f"Missing part: {part}"

#     # Should have connections for:
#     # - VIN to regulator input and monitoring
#     # - 3V3 output to monitoring
#     # - GND connections
#     expected_nets = ["vin", "3v3", "gnd", "5v_monitor", "3v3_monitor"]
#     for net in expected_nets:
#         assert net.lower() in code.lower(), f"Missing net: {net}"