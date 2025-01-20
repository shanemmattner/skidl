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
            
        component_pins[component.properties[0].value].sort(
            key=lambda x: int(x['pin_number'])
        )
    
    return component_pins
