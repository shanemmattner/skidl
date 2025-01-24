import pytest
from skidl import *

def test_parse_netlist_section():
    """Test parsing the netlist section to identify connections"""
    netlist_text = """=== Netlist ===
GND:
    #PWR028 Pin 1 (~)
    C10 Pin 2 (~)
    #PWR025 Pin 1 (~)
    R10 Pin 2 (~)
    Power Labels:
        GND
VOUT:
    R10 Pin 1 (~)
    R9 Pin 2 (~)
    C10 Pin 1 (~)
    Hierarchical Labels:
        VOUT
VIN:
    R9 Pin 1 (~)
    Hierarchical Labels:
        VIN"""
    
    # This should return a dict of net connections
    expected_nets = {
        'GND': {
            'pins': ['C10.2', 'R10.2'],
            'type': 'power'
        },
        'VOUT': {
            'pins': ['R10.1', 'R9.2', 'C10.1'],
            'type': 'hierarchical'
        },
        'VIN': {
            'pins': ['R9.1'],
            'type': 'hierarchical'
        }
    }
    
    # Test function would parse netlist text into this structure
    parsed_nets = parse_netlist(netlist_text)
    assert parsed_nets == expected_nets

def test_parse_components_section():
    """Test parsing the components section"""
    components_text = """=== Components ===
Component: Device/R
    Properties:
        Reference: R10
        Value: 1k
        Footprint: Resistor_SMD:R_0603_1608Metric
        Datasheet: ~
        Description: Resistor
    Position: (121.92, 81.28), Angle: 0
Unit: 1"""

    expected_component = {
        'library': 'Device',
        'part': 'R',
        'reference': 'R10',
        'value': '1k',
        'footprint': 'Resistor_SMD:R_0603_1608Metric'
    }

    parsed_component = parse_component(components_text)
    assert parsed_component == expected_component

def test_generate_skidl_code():
    """Test generating SKiDL code from parsed components and nets"""
    components = [
        {
            'library': 'Device',
            'part': 'R',
            'reference': 'R9',
            'value': '2k'
        },
        {
            'library': 'Device', 
            'part': 'R',
            'reference': 'R10',
            'value': '1k'
        },
        {
            'library': 'Device',
            'part': 'C', 
            'reference': 'C10',
            'value': '100nF'
        }
    ]
    
    nets = {
        'GND': {
            'pins': ['C10.2', 'R10.2'],
            'type': 'power'
        },
        'VOUT': {
            'pins': ['R10.1', 'R9.2', 'C10.1'],
            'type': 'hierarchical'
        },
        'VIN': {
            'pins': ['R9.1'],
            'type': 'hierarchical'
        }
    }

    expected_code = """@subcircuit
def resistor_divider(vin, vout, gnd):
    # Create components
    r9 = Part('Device', 'R', value='2k')
    r10 = Part('Device', 'R', value='1k')
    c10 = Part('Device', 'C', value='100nF')
    
    # Connect components
    vin += r9[1]
    r9[2] += r10[1], c10[1], vout
    r10[2] += c10[2], gnd"""

    generated_code = generate_skidl_code(components, nets)
    assert generated_code.strip() == expected_code.strip()

def test_full_conversion():
    """Test the full conversion from text to working SKiDL code"""
    with open('resistor_divider_output.txt', 'r') as f:
        circuit_text = f.read()

    # Generate SKiDL code
    skidl_code = convert_to_skidl(circuit_text)
    
    # Execute the generated code and verify circuit
    exec(skidl_code)
    
    # Create test circuit
    vin = Net('VIN')
    vout = Net('VOUT')
    gnd = Net('GND')
    
    # Instantiate the generated circuit
    resistor_divider(vin, vout, gnd)
    
    # Verify correct connections
    assert len(vin.pins) == 1
    assert len(vout.pins) == 3  # Connected to R9, R10, C10
    assert len(gnd.pins) == 2   # Connected to R10, C10
    
    # Verify values
    r9 = None
    for part in default_circuit.parts:
        if part.ref == 'R9':
            r9 = part
            break
    assert r9.value == '2k'

def test_handle_power_labels():
    """Test handling of power labels like GND"""
    power_text = """Power Labels:
    GND at (121.92, 85.09)
    GND at (138.43, 81.28)"""
    
    power_nets = parse_power_labels(power_text)
    assert 'GND' in power_nets
    assert len(power_nets['GND']) == 2

def test_handle_hierarchical_labels():
    """Test handling of hierarchical labels"""
    hier_text = """Hierarchical Labels and Sheet Pins:
    Label: VIN (input) at (121.92, 59.69)
    Label: VOUT (input) at (138.43, 73.66)"""
    
    hier_labels = parse_hierarchical_labels(hier_text)
    assert 'VIN' in hier_labels
    assert 'VOUT' in hier_labels
    assert hier_labels['VIN']['type'] == 'input'