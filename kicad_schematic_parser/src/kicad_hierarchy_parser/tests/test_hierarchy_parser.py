from kiutils.schematic import Schematic, HierarchicalSheet, HierarchicalPin, Position, Property, Effects
from kicad_hierarchy_parser.components.component_parser import calculate_pin_position, find_symbol_definition, get_component_pins

def test_symbol_definition_parsing():
    """Test parsing of symbol definitions"""
    schematic = Schematic()
    
    # Simulate a schematic with a component
    class MockLibSymbol:
        def __init__(self):
            self.name = 'TEST_SYMBOL'
            self.pins = [
                type('MockPin', (), {
                    'name': 'VCC',
                    'electricalType': 'power_in',
                    'position': type('MockPosition', (), {'x': 0, 'y': 2.54})()
                }),
                type('MockPin', (), {
                    'name': 'GND',
                    'electricalType': 'power_in',
                    'position': type('MockPosition', (), {'x': 0, 'y': -2.54})()
                })
            ]
    
    # Simulate library symbols
    schematic.libSymbols = [MockLibSymbol()]
    
    # Test symbol definition finding
    symbol = find_symbol_definition(schematic, 'TEST_SYMBOL')
    assert symbol is not None, "Symbol definition not found"
    assert symbol.name == 'TEST_SYMBOL', "Incorrect symbol name"
    assert len(symbol.pins) == 2, "Incorrect number of pins"
    
    # Test pin position calculation
    class MockComponent:
        def __init__(self):
            self.position = Position(X=100, Y=200, angle=0)
    
    component = MockComponent()
    
    # Test VCC pin
    vcc_pin = symbol.pins[0]
    vcc_pos = calculate_pin_position(component, vcc_pin)
    assert vcc_pos[0] == 100, "Incorrect X position for VCC pin"
    assert vcc_pos[1] == 202.54, "Incorrect Y position for VCC pin"
    
    # Test GND pin
    gnd_pin = symbol.pins[1]
    gnd_pos = calculate_pin_position(component, gnd_pin)
    assert gnd_pos[0] == 100, "Incorrect X position for GND pin"
    assert gnd_pos[1] == 197.46, "Incorrect Y position for GND pin"

def test_component_pin_extraction():
    """Test extraction of component pins from a schematic"""
    # Create a mock schematic with components
    schematic = Schematic()
    
    # Simulate components and their pins
    class MockComponent:
        def __init__(self, ref, symbol_name, position):
            self.reference = ref
            self.symbolName = symbol_name
            self.position = position
    
    class MockLibSymbol:
        def __init__(self, name, pins):
            self.name = name
            self.pins = pins
    
    # Create mock library symbols
    mock_symbols = [
        MockLibSymbol('RESISTOR', [
            type('MockPin', (), {
                'name': '1',
                'electricalType': 'passive',
                'position': type('MockPosition', (), {'x': -2.54, 'y': 0})()
            }),
            type('MockPin', (), {
                'name': '2',
                'electricalType': 'passive',
                'position': type('MockPosition', (), {'x': 2.54, 'y': 0})()
            })
        ])
    ]
    
    schematic.libSymbols = mock_symbols
    
    # Add mock components
    schematic.components = [
        MockComponent('R1', 'RESISTOR', Position(X=100, Y=200, angle=0)),
        MockComponent('R2', 'RESISTOR', Position(X=150, Y=250, angle=90))
    ]
    
    # Extract component pins
    component_pins = get_component_pins(schematic)
    
    # Verify pin extraction
    assert 'R1' in component_pins, "R1 not found in component pins"
    assert 'R2' in component_pins, "R2 not found in component pins"
    
    # Check R1 pins
    r1_pins = component_pins['R1']
    assert len(r1_pins) == 2, "Incorrect number of pins for R1"
    
    # Check R2 pins
    r2_pins = component_pins['R2']
    assert len(r2_pins) == 2, "Incorrect number of pins for R2"
