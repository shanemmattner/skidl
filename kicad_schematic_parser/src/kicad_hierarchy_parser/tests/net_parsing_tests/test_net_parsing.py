import os
import pytest
from kiutils.schematic import Schematic
from kicad_hierarchy_parser.parser import analyze_schematic
from kicad_hierarchy_parser.connectivity.net_parser import calculate_pin_connectivity

@pytest.fixture
def schematic_parser():
    def _parser(schematic_path):
        base_path = os.path.dirname(os.path.abspath(schematic_path))
        schematic = Schematic().from_file(schematic_path)
        result = analyze_schematic(schematic, base_path)
        
        # Collect components, wire connections, and labels from all schematics
        all_components = {}
        all_wire_connections = []
        all_labels = {'power': [], 'hierarchical': [], 'local': []}
        
        for sch in result:
            # Collect components
            from kicad_hierarchy_parser.components.component_parser import get_component_pins
            all_components.update(get_component_pins(sch))
            
            # Collect wire connections
            from kicad_hierarchy_parser.connectivity.wire_parser import get_wire_connections
            all_wire_connections.extend(get_wire_connections(sch))
            
            # Collect labels
            from kicad_hierarchy_parser.labels.label_parser import parse_labels
            labels = parse_labels(sch)
            all_labels['power'].extend(labels['power'])
            all_labels['hierarchical'].extend(labels['hierarchical'])
            all_labels['local'].extend(labels['local'])
        
        return (
            all_components,
            all_wire_connections,
            all_labels
        )
    return _parser

def test_resistor_divider(schematic_parser):
    """Test basic resistor divider circuit net parsing"""
    components, wires, labels = schematic_parser('/Users/shanemattner/Desktop/skidl/kicad_schematic_parser/example_kicad_project/resistor_divider.kicad_sch')
    netlist = calculate_pin_connectivity(components, wires, labels)
    
    # Verify expected nets exist
    assert 'VIN' in netlist
    assert 'VOUT' in netlist
    assert 'GND' in netlist
    
    # Verify pin connections
    assert len(netlist['GND']['pins']) == 3
    assert len(netlist['VIN']['pins']) == 2
    assert len(netlist['VOUT']['pins']) == 3

def test_power_supply(schematic_parser):
    """Test power supply circuit with multiple voltage rails"""
    components, wires, labels = schematic_parser('/Users/shanemattner/Desktop/skidl/kicad_schematic_parser/example_kicad_project/power2.kicad_sch')
    netlist = calculate_pin_connectivity(components, wires, labels)
    
    assert '3V3' in netlist
    assert '5V' in netlist
    assert 'GND' in netlist
    assert len(netlist['GND']['pins']) > 5
