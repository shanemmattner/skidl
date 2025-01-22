import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from skidl_kicad_parser.components.component_parser import calculate_pin_position, find_symbol_definition, get_component_pins

def test_calculate_pin_position():
    """Test pin position calculation with data from hierarchy.txt"""
    class Position:
        def __init__(self, x, y, angle=0):
            self.X = x
            self.Y = y
            self.angle = angle
    
    # Test case from hierarchy.txt - U3 (ESP32-S3-MINI-1) IO0 pin
    component_pos = Position(179.07, 96.52, 0)
    pin_pos = Position(163.83, 76.20)
    
    absolute_x, absolute_y = calculate_pin_position(component_pos, pin_pos)
    
    # Verify position matches hierarchy.txt data
    assert round(absolute_x, 2) == 163.83
    assert round(absolute_y, 2) == 76.20

def test_calculate_pin_position_with_rotation():
    """Test that pin positions remain absolute regardless of component rotation"""
    class Position:
        def __init__(self, x, y, angle=0):
            self.X = x
            self.Y = y
            self.angle = angle
    
    # Test with rotated component - pin positions should remain absolute
    component_pos = Position(100.0, 100.0, 90)  # Component rotation doesn't affect absolute pin positions
    pin_pos = Position(163.83, 76.20)  # Using real data from hierarchy.txt
    
    absolute_x, absolute_y = calculate_pin_position(component_pos, pin_pos)
    
    # Pin position should remain absolute regardless of component rotation
    assert round(absolute_x, 2) == 163.83
    assert round(absolute_y, 2) == 76.20

def test_component_pin_electrical_types():
    """Test electrical type extraction from hierarchy.txt data"""
    class MockPin:
        def __init__(self, number, name, position, electrical_type):
            self.number = number
            self.name = name
            self.position = position
            self.electricalType = electrical_type
            self.alternatePins = []
    
    class MockUnit:
        def __init__(self, pins):
            self.pins = pins
    
    class MockSymbol:
        def __init__(self, lib_nickname, entry_name, pins):
            self.libraryNickname = lib_nickname
            self.entryName = entry_name
            self.units = [MockUnit(pins)]
    
    class MockComponent:
        def __init__(self, lib_nickname, entry_name, ref, position):
            self.libraryNickname = lib_nickname
            self.entryName = entry_name
            self.properties = [type('obj', (), {'value': ref})]
            self.position = position
    
    class Position:
        def __init__(self, x, y, angle=0):
            self.X = x
            self.Y = y
            self.angle = angle
    
    # Mock data from hierarchy.txt - U3 (ESP32-S3-MINI-1)
    pins = [
        MockPin('1', 'GND', Position(179.07, 127.00), 'power_in'),
        MockPin('3', '3V3', Position(179.07, 66.04), 'power_in'),
        MockPin('4', 'IO0', Position(163.83, 76.20), 'bidirectional')
    ]
    
    symbol = MockSymbol('RF_Module', 'ESP32-S3-MINI-1', pins)
    component = MockComponent('RF_Module', 'ESP32-S3-MINI-1', 'U3', Position(179.07, 96.52, 0))
    
    class MockSchematic:
        def __init__(self):
            self.libSymbols = [symbol]
            self.schematicSymbols = [component]
    
    schematic = MockSchematic()
    component_pins = get_component_pins(schematic)
    
    # Verify pin data
    assert 'U3' in component_pins
    pins = component_pins['U3']
    
    # Check GND pin
    gnd_pin = next(p for p in pins if p['pin_number'] == '1')
    assert gnd_pin['pin_name'] == 'GND'
    assert gnd_pin['electrical_type'] == 'power_in'
    
    # Check IO0 pin
    io_pin = next(p for p in pins if p['pin_number'] == '4')
    assert io_pin['pin_name'] == 'IO0'
    assert io_pin['electrical_type'] == 'bidirectional'

if __name__ == '__main__':
    pytest.main([__file__])
