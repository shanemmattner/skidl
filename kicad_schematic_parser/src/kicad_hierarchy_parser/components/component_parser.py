import math

def calculate_pin_position(component_position, pin_position, component_angle=0):
    """
    Transform pin position from component-relative to absolute coordinates
    
    Args:
        component_position: Component's position in schematic
        pin_position: Pin's position relative to component origin
        component_angle: Component's rotation angle in degrees
    
    Returns:
        tuple: Absolute (x,y) position of pin in schematic coordinates
    """
    # Convert angle to radians
    angle_rad = math.radians(component_angle)
    
    # Get pin position relative to component
    rel_x = float(pin_position.X)
    rel_y = float(pin_position.Y)
    
    # Rotate pin position if component is rotated
    if component_angle != 0:
        rot_x = rel_x * math.cos(angle_rad) - rel_y * math.sin(angle_rad)
        rot_y = rel_x * math.sin(angle_rad) + rel_y * math.cos(angle_rad)
        rel_x = rot_x
        rel_y = rot_y
    
    # Add component position to get absolute coordinates
    abs_x = float(component_position.X) + rel_x
    abs_y = float(component_position.Y) + rel_y
    
    return (abs_x, abs_y)

def find_symbol_definition(schematic, lib_nickname, entry_name):
    """
    Find symbol definition from library symbols
    """
    for symbol in schematic.libSymbols:
        if (symbol.libraryNickname == lib_nickname and 
            symbol.entryName == entry_name):
            return symbol
    return None


def natural_sort_key(pin_info):
    """
    Create a natural sort key for pin numbers that can handle both 
    numeric (1,2,3) and alphanumeric (A1, B1, etc) pin numbers
    """
    pin_num = pin_info['pin_number']
    # Handle pure numeric values
    try:
        return (0, int(pin_num))  # Pure numbers come first
    except ValueError:
        # Handle alphanumeric values like 'A1', 'B1'
        # Extract any numeric portion for secondary sorting
        numeric_part = ''.join(c for c in pin_num if c.isdigit())
        alpha_part = ''.join(c for c in pin_num if c.isalpha())
        return (1, alpha_part, int(numeric_part) if numeric_part else 0)

def get_component_pins(schematic):
    """
    Extract and calculate absolute positions for all component pins in the schematic
    """
    component_pins = {}
    
    for component in schematic.schematicSymbols:
        symbol_def = find_symbol_definition(
            schematic, 
            component.libraryNickname, 
            component.entryName
        )
        
        if not symbol_def:
            continue
            
        pins = []
        for unit in symbol_def.units:
            if hasattr(unit, 'pins'):
                pins.extend(unit.pins)
        
        component_pins[component.properties[0].value] = []
        
        for pin in pins:
            absolute_pos = calculate_pin_position(
                component.position,
                pin.position,
                component.position.angle
            )
            pin_info = {
                'pin_number': pin.number,
                'pin_name': pin.name,
                'absolute_position': absolute_pos,
                'electrical_type': pin.electricalType,
                'alternatePins': [
                    {
                        'pinName': alt.pinName,
                        'electricalType': alt.electricalType
                    } for alt in pin.alternatePins
                ] if hasattr(pin, 'alternatePins') else []
            }
            component_pins[component.properties[0].value].append(pin_info)
            
        # Use natural sort for the pin numbers
        component_pins[component.properties[0].value].sort(
            key=natural_sort_key
        )
    
    return component_pins
