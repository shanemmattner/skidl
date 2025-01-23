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
    expected_3v3_monitor = {
        ("J2", "2"),  # Pin 2 of J2
        ("R6", "1"),  # Pin 1 of R6
        ("C8", "1"),  # Pin 1 of C8
        ("R5", "2")   # Pin 2 of R5
    }
    assert set((comp["component"], comp["pin_number"]) for comp in three_v3_monitor["pins"]) == expected_3v3_monitor
    assert "3v3_monitor" in three_v3_monitor["hierarchical_labels"]

    # Test GND connections
    gnd = netlist["GND"]
    expected_gnd = {
        ("R8", "2"),
        ("R6", "2"),
        ("C7", "2"),
        ("C6", "2"),
        ("U3", "1"),  # GND pin
        ("R4", "2"),
        ("J2", "4"),  # Pin 4
        ("C5", "2"),
        ("C8", "2"),
        ("#PWR023", "1"),  # Power symbols
        ("#PWR020", "1"),
        ("#PWR019", "1"),
        ("#PWR017", "1"),
        ("#PWR015", "1"),
        ("#PWR018", "1"),
        ("#PWR022", "1"),
        ("#PWR010", "1"),
        ("#PWR021", "1")
    }
    assert set((comp["component"], comp["pin_number"]) for comp in gnd["pins"]) == expected_gnd
    assert "GND" in gnd["power_labels"]

    # Test +5V connections
    five_v = netlist["+5V"]
    expected_5v = {
        ("R7", "1"),
        ("C5", "1"),
        ("U3", "3"),  # VI pin
        ("R3", "1"),
        ("#PWR024", "1"),  # Power symbols
        ("#PWR03", "1")
    }
    assert set((comp["component"], comp["pin_number"]) for comp in five_v["pins"]) == expected_5v
    assert "+5V" in five_v["power_labels"]

    # Test divider_2 connections
    divider = netlist["divider_2"]
    expected_divider = {
        ("R8", "1"),
        ("R7", "2"),
        ("J2", "3")  # Pin 3
    }
    assert set((comp["component"], comp["pin_number"]) for comp in divider["pins"]) == expected_divider
    assert "divider_2" in divider["local_labels"]

    # Test 5v_monitor connections
    five_v_monitor = netlist["5v_monitor"]
    expected_5v_monitor = {
        ("J2", "1"),  # Pin 1
        ("R4", "1"),
        ("C7", "1"),
        ("R3", "2")
    }
    assert set((comp["component"], comp["pin_number"]) for comp in five_v_monitor["pins"]) == expected_5v_monitor
    assert "5v_monitor" in five_v_monitor["hierarchical_labels"]

    # Test +3V3 connections
    three_v3 = netlist["+3V3"]
    expected_3v3 = {
        ("R5", "1"),
        ("U3", "2"),  # VO pin
        ("C6", "1"),
        ("#PWR016", "1")  # Power symbol
    }
    assert set((comp["component"], comp["pin_number"]) for comp in three_v3["pins"]) == expected_3v3
    assert "+3V3" in three_v3["power_labels"]
