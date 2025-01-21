import math

def calculate_pin_position(component_position, pin_position, component_angle=0):
    """
    Calculate absolute pin position based on component position and relative pin position
    """
    angle_rad = math.radians(component_angle)
    
    # Apply rotation
    rotated_x = pin_position.X * math.cos(angle_rad) - pin_position.Y * math.sin(angle_rad)
    rotated_y = pin_position.X * math.sin(angle_rad) + pin_position.Y * math.cos(angle_rad)
    
    # Add component position
    absolute_x = component_position.X + rotated_x
    absolute_y = component_position.Y - rotated_y
    
    return (absolute_x, absolute_y)

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

