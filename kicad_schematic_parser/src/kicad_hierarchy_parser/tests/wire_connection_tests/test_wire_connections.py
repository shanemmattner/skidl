import pytest
from kiutils.schematic import Schematic
import math
import os
from kicad_hierarchy_parser.components.component_parser import get_component_pins
from kicad_hierarchy_parser.connectivity.net_parser import calculate_pin_connectivity
from kicad_hierarchy_parser.connectivity.wire_parser import get_wire_connections
from kicad_hierarchy_parser.labels.label_parser import parse_labels

# Test data directory
TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def test_wire_connections():
    """Test wire connections from wire_conn_test.kicad_sch"""
    schematic = Schematic().from_file(os.path.join(TEST_DATA_DIR, "wire_conn_test.kicad_sch"))
    component_pins = get_component_pins(schematic)
    wire_connections = get_wire_connections(schematic)
    labels = parse_labels(schematic)
    netlist = calculate_pin_connectivity(component_pins, wire_connections, labels)

    # Test specific net connections
    assert "3v3_monitor" in netlist, "3v3_monitor net missing"
    assert "GND" in netlist, "GND net missing"
    assert "+5V" in netlist, "5V net missing"
    assert "divider_2" in netlist, "divider_2 net missing"
    assert "5v_monitor" in netlist, "5v_monitor net missing"
    assert "+3V3" in netlist, "+3V3 net missing"

    # Test 3v3_monitor connections
    three_v3_monitor = netlist["3v3_monitor"]
    # NOTE: These connections for resistors and capacitors are opposite of the expected order
    expected_3v3_monitor = {
        ('J1', '2'),      # Pin 2 of connector J1
        ('R5', '2'),      # Top pin of R5 (voltage divider)
        ('R6', '1'),      # Top pin of R6
        ('C4', '2')       # Top pin of C4 (filtering cap)
    }
    assert set((comp["component"], comp["pin_number"]) for comp in three_v3_monitor["pins"]) == expected_3v3_monitor