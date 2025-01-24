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

def parse_skidl_code(code: str) -> dict:
    """Parse SKiDL code and return structured representation of components and connections."""
    result = {
        'components': set(),  # Set of (library, part, value) tuples
        'connections': [],    # List of sets of connected pins/nets
    }
    
    # Split into lines and remove empty ones
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    for line in lines:
        # Parse component definitions
        if '=' in line and 'Part' in line:
            # Extract component info using string manipulation
            parts = line.split("'")  # Split on quotes to get library and part
            library = parts[1]
            part = parts[3]
            value = parts[5] if len(parts) > 5 else ''
            result['components'].add((library, part, value))
            
        # Parse connections
        elif '+=' in line:
            # Remove spaces around operators and split on commas
            line = line.replace(' += ', '+=')
            parts = set()
            
            # Split at += to get left and right sides
            left, right = line.split('+=')
            left = left.strip()
            if left:  # Add the left side pin if it exists
                parts.add(left.strip())
                
            # Add right side components/nets
            right_parts = [p.strip() for p in right.split(',')]
            parts.update(right_parts)
            
            # Remove any empty strings
            parts = {p for p in parts if p}
            if parts:
                result['connections'].append(parts)
    
    return result

def are_circuits_equivalent(code1: str, code2: str) -> bool:
    """Compare two SKiDL circuit descriptions for functional equivalence."""
    # Parse both circuits
    circuit1 = parse_skidl_code(code1)
    circuit2 = parse_skidl_code(code2)
    
    # Check if components match
    if circuit1['components'] != circuit2['components']:
        print("Components don't match:")
        print(f"Circuit 1: {circuit1['components']}")
        print(f"Circuit 2: {circuit2['components']}")
        return False
        
    # Check if all connections are equivalent
    # First normalize the connections by converting to frozenset for comparison
    connections1 = {frozenset(conn) for conn in circuit1['connections']}
    connections2 = {frozenset(conn) for conn in circuit2['connections']}
    
    if connections1 != connections2:
        print("Connections don't match:")
        print(f"Circuit 1: {connections1}")
        print(f"Circuit 2: {connections2}")
        return False
        
    return True

def test_resistor_divider_skidl_generation():
    """Test generating SKiDL code from real resistor divider example."""
    code = sheet_to_skidl("resistor_divider", RESISTOR_DIVIDER_TEXT)
    
    print("\n=== Generated Code ===")
    print(code)
    
    # Split into sections for debugging
    gen_lines = code.split('\n')
    component_lines = [l for l in gen_lines if 'Part(' in l]
    connection_lines = [l for l in gen_lines if '+=' in l]
    
    print("\n=== Component Lines ===")
    print('\n'.join(component_lines))
    
    print("\n=== Connection Lines ===")
    print('\n'.join(connection_lines))
    
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
    
    print("\n=== Expected Component Lines ===")
    exp_lines = expected_code.split('\n')
    exp_component_lines = [l for l in exp_lines if 'Part(' in l]
    print('\n'.join(exp_component_lines))
    
    print("\n=== Expected Connection Lines ===")
    exp_connection_lines = [l for l in exp_lines if '+=' in l]
    print('\n'.join(exp_connection_lines))

    # Instead of exact string matching, check for circuit equivalence
    assert are_circuits_equivalent(code, expected_code), \
        "Generated circuit is not functionally equivalent to expected circuit"
