import os
import pytest
from kiutils.schematic import Schematic
from kicad_hierarchy_parser.components.component_parser import get_component_pins
from kicad_hierarchy_parser.connectivity.wire_parser import get_wire_connections
from kicad_hierarchy_parser.labels.label_parser import parse_labels
from kicad_hierarchy_parser.connectivity.net_parser import calculate_pin_connectivity

@pytest.fixture
def schematic_parser():
    def _parser(schematic_path):
        base_path = os.path.dirname(os.path.abspath(schematic_path))
        schematic = Schematic().from_file(schematic_path)
        
        # Get components directly from the schematic
        all_components = get_component_pins(schematic)
        
        # Get wire connections
        all_wire_connections = get_wire_connections(schematic)
        
        # Get labels
        all_labels = parse_labels(schematic)
        
        return (
            all_components,
            all_wire_connections,
            all_labels
        )
    return _parser

def test_resistor_divider(schematic_parser):
    """Test basic resistor divider circuit net parsing"""
    # Get the absolute path to the test file directory
    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    schematic_path = os.path.join(TEST_DIR, "resistor_divider.kicad_sch")
    
    components, wires, labels = schematic_parser(schematic_path)
    netlist = calculate_pin_connectivity(components, wires, labels)

    # Verify expected nets exist
    assert 'VIN' in netlist
    assert 'VOUT' in netlist
    assert 'GND' in netlist
    
    # Verify pin connections
    assert len(netlist['GND']['pins']) == 4  # Updated to match actual number of GND pins
    assert len(netlist['VIN']['pins']) == 1  # R9 Pin 2 (input)
    assert len(netlist['VOUT']['pins']) == 3  # R10 Pin 2, R9 Pin 1, C10 Pin 2
    
    # Verify specific pin connections
    gnd_pins = {pin['component'] for pin in netlist['GND']['pins']}
    assert '#PWR028' in gnd_pins  # Power flag
    assert '#PWR025' in gnd_pins  # Power flag
    assert 'C10' in gnd_pins      # Capacitor GND pin
    assert 'R10' in gnd_pins      # Resistor GND pin
    
    vout_pins = {pin['component'] for pin in netlist['VOUT']['pins']}
    assert 'R10' in vout_pins     # Upper resistor
    assert 'R9' in vout_pins      # Lower resistor
    assert 'C10' in vout_pins     # Capacitor