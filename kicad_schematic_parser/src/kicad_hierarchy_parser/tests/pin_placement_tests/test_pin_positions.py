import pytest
from kiutils.schematic import Schematic
import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from kicad_hierarchy_parser.components.component_parser import (
    get_component_pins,
    find_symbol_definition
)

# Test data directory
TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# def test_power2_schematic_pins():
#     """Test pin extraction from power2.kicad_sch"""
#     schematic = Schematic().from_file(os.path.join(TEST_DATA_DIR, "power2.kicad_sch"))
#     component_pins = get_component_pins(schematic)
    
#     # Expected positions for each component
#     expected_positions = {
#         "#PWR012": [(73.66, 74.93, "power_in")],  # Pin 1
#         "#PWR09": [(107.95, 74.93, "power_in")],  # Pin 1
#         "U1": [
#             (90.17, 71.12, "power_in"),   # Pin 1 (GND)
#             (97.79, 63.50, "power_out"),  # Pin 2 (VO)
#             (82.55, 63.50, "power_in")    # Pin 3 (VI)
#         ],
#         "C2": [
#             (107.95, 63.50, "passive"),  # Pin 1
#             (107.95, 71.12, "passive")   # Pin 2
#         ],
#         "C3": [
#             (73.66, 63.50, "passive"),  # Pin 1
#             (73.66, 71.12, "passive")   # Pin 2
#         ],
#         "#PWR011": [(73.66, 63.50, "power_in")],  # Pin 1
#         "#PWR08": [(107.95, 63.50, "power_in")],  # Pin 1
#         "#PWR06": [(90.17, 74.93, "power_in")]    # Pin 1
#     }
    
#     # Test each component's pins
#     for component_ref, expected_pins in expected_positions.items():
#         pins = component_pins.get(component_ref, [])
#         assert len(pins) == len(expected_pins), f"Wrong number of pins for {component_ref}"
        
#         for pin, (exp_x, exp_y, exp_type) in zip(pins, expected_pins):
#             assert math.isclose(pin['absolute_position'][0], exp_x, rel_tol=1e-2), \
#                 f"Wrong X position for {component_ref} pin {pin['pin_number']}"
#             assert math.isclose(pin['absolute_position'][1], exp_y, rel_tol=1e-2), \
#                 f"Wrong Y position for {component_ref} pin {pin['pin_number']}"
#             assert pin['electrical_type'] == exp_type, \
#                 f"Wrong electrical type for {component_ref} pin {pin['pin_number']}"

def test_resistor_divider_schematic_pins():
    """Test pin extraction from resistor_divider.kicad_sch"""
    schematic = Schematic().from_file(os.path.join(TEST_DATA_DIR, "resistor_divider.kicad_sch"))
    component_pins = get_component_pins(schematic)
    
    # Expected positions for each component
    expected_positions = {
        "#PWR04": [(121.92, 85.09, "power_in")],  # Pin 1
        "#PWR07": [(138.43, 81.28, "power_in")],  # Pin 1
        "R2": [
            (121.92, 85.09, "passive"),   # Pin 2
            (121.92, 77.47, "passive")  # Pin 1
        ],
        "R1": [
            (121.92, 67.31, "passive"),   # Pin 2
            (121.92, 59.69, "passive")  # Pin 1
            
        ],
        "C4": [
            (138.43, 81.28, "passive"),   # Pin 2
            (138.43, 73.66, "passive")  # Pin 1
            
        ]
    }
    
    # Test each component's pins
    for component_ref, expected_pins in expected_positions.items():
        pins = component_pins.get(component_ref, [])
        assert len(pins) == len(expected_pins), f"Wrong number of pins for {component_ref}"
        
        for pin, (exp_x, exp_y, exp_type) in zip(pins, expected_pins):
            assert math.isclose(pin['absolute_position'][0], exp_x, rel_tol=1e-2), \
                f"Wrong X position for {component_ref} pin {pin['pin_number']}"
            assert math.isclose(pin['absolute_position'][1], exp_y, rel_tol=1e-2), \
                f"Wrong Y position for {component_ref} pin {pin['pin_number']}"
            assert pin['electrical_type'] == exp_type, \
                f"Wrong electrical type for {component_ref} pin {pin['pin_number']}"

# def test_stm32_schematic_pins():
#     """Test pin extraction from stm32.kicad_sch"""
#     schematic = Schematic().from_file(os.path.join(TEST_DATA_DIR, "stm32.kicad_sch"))
#     component_pins = get_component_pins(schematic)
    
#     # Expected positions for each component
#     expected_positions = {
#         "#PWR02": [(102.87, 33.02, "power_in")],
#         "J1": [
#             (161.29, 45.72, "passive"),  # Pin 1
#             (161.29, 48.26, "passive"),  # Pin 2
#             (161.29, 50.80, "passive"),  # Pin 3
#             (161.29, 53.34, "passive")   # Pin 4
#         ],
#         "C1": [
#             (102.87, 25.40, "passive"),  # Pin 1
#             (102.87, 33.02, "passive")   # Pin 2
#         ],
#         "U2": [
#             (115.57, 36.83, "power_in"),      # Pin 1 (VBAT)
#             (102.87, 69.85, "bidirectional"), # Pin 2 (PC13)
#             (102.87, 72.39, "bidirectional"), # Pin 3 (PC14)
#             (102.87, 74.93, "bidirectional"), # Pin 4 (PC15)
#             (102.87, 52.07, "bidirectional"), # Pin 5 (PF0)
#             (102.87, 54.61, "bidirectional"), # Pin 6 (PF1)
#             (102.87, 46.99, "bidirectional"), # Pin 7 (PG10)
#             (135.89, 41.91, "bidirectional"), # Pin 8 (PA0)
#             (135.89, 44.45, "bidirectional"), # Pin 9 (PA1)
#             (135.89, 46.99, "bidirectional"), # Pin 10 (PA2)
#             (135.89, 49.53, "bidirectional"), # Pin 11 (PA3)
#             (135.89, 52.07, "bidirectional"), # Pin 12 (PA4)
#             (135.89, 54.61, "bidirectional"), # Pin 13 (PA5)
#             (135.89, 57.15, "bidirectional"), # Pin 14 (PA6)
#             (135.89, 59.69, "bidirectional"), # Pin 15 (PA7)
#             (102.87, 59.69, "bidirectional"), # Pin 16 (PC4)
#             (102.87, 80.01, "bidirectional"), # Pin 17 (PB0)
#             (102.87, 82.55, "bidirectional"), # Pin 18 (PB1)
#             (102.87, 85.09, "bidirectional"), # Pin 19 (PB2)
#             (102.87, 41.91, "input"),         # Pin 20 (VREF+)
#             (125.73, 36.83, "power_in"),      # Pin 21 (VDDA)
#             (102.87, 105.41, "bidirectional"), # Pin 22 (PB10)
#             (118.11, 36.83, "power_in"),      # Pin 23 (VDD)
#             (102.87, 107.95, "bidirectional"), # Pin 24 (PB11)
#             (102.87, 110.49, "bidirectional"), # Pin 25 (PB12)
#             (102.87, 113.03, "bidirectional"), # Pin 26 (PB13)
#             (102.87, 115.57, "bidirectional"), # Pin 27 (PB14)
#             (102.87, 118.11, "bidirectional"), # Pin 28 (PB15)
#             (102.87, 62.23, "bidirectional"), # Pin 29 (PC6)
#             (135.89, 62.23, "bidirectional"), # Pin 30 (PA8)
#             (135.89, 64.77, "bidirectional"), # Pin 31 (PA9)
#             (135.89, 67.31, "bidirectional"), # Pin 32 (PA10)
#             (135.89, 69.85, "bidirectional"), # Pin 33 (PA11)
#             (135.89, 72.39, "bidirectional"), # Pin 34 (PA12)
#             (120.65, 36.83, "power_in"),      # Pin 35 (VDD)
#             (135.89, 74.93, "bidirectional"), # Pin 36 (PA13)
#             (135.89, 77.47, "bidirectional"), # Pin 37 (PA14)
#             (135.89, 80.01, "bidirectional"), # Pin 38 (PA15)
#             (102.87, 64.77, "bidirectional"), # Pin 39 (PC10)
#             (102.87, 67.31, "bidirectional"), # Pin 40 (PC11)
#             (102.87, 87.63, "bidirectional"), # Pin 41 (PB3)
#             (102.87, 90.17, "bidirectional"), # Pin 42 (PB4)
#             (102.87, 92.71, "bidirectional"), # Pin 43 (PB5)
#             (102.87, 95.25, "bidirectional"), # Pin 44 (PB6)
#             (102.87, 97.79, "bidirectional"), # Pin 45 (PB7)
#             (102.87, 100.33, "bidirectional"), # Pin 46 (PB8)
#             (102.87, 102.87, "bidirectional"), # Pin 47 (PB9)
#             (123.19, 36.83, "power_in"),      # Pin 48 (VDD)
#             (120.65, 125.73, "power_in")      # Pin 49 (VSS)
#         ],
#         "#PWR014": [(161.29, 48.26, "power_in")],
#         "#PWR013": [(161.29, 45.72, "power_in")],
#         "#PWR01": [(102.87, 25.40, "power_in")],
#         "#PWR05": [(120.65, 125.73, "power_in")]
#     }
    
#     # Test each component's pins
#     for component_ref, expected_pins in expected_positions.items():
#         pins = component_pins.get(component_ref, [])
#         assert len(pins) == len(expected_pins), f"Wrong number of pins for {component_ref}"
        
#         for pin, (exp_x, exp_y, exp_type) in zip(pins, expected_pins):
#             assert math.isclose(pin['absolute_position'][0], exp_x, rel_tol=1e-2), \
#                 f"Wrong X position for {component_ref} pin {pin['pin_number']}"
#             assert math.isclose(pin['absolute_position'][1], exp_y, rel_tol=1e-2), \
#                 f"Wrong Y position for {component_ref} pin {pin['pin_number']}"
#             assert pin['electrical_type'] == exp_type, \
#                 f"Wrong electrical type for {component_ref} pin {pin['pin_number']}"
