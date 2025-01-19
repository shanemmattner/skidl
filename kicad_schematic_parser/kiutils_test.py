from kiutils.schematic import Schematic
import math
import sys

def parse_labels(schematic):
    """
    Parse different types of labels from the schematic
    """
    labels = {
        'local': [],
        'hierarchical': [],
        'power': []
    }
    
    # Parse local labels
    for label in schematic.labels:
        label_info = {
            'text': label.text,
            'position': (label.position.X, label.position.Y),
            'angle': label.position.angle
        }
        labels['local'].append(label_info)
        
    # Parse hierarchical labels
    for label in schematic.hierarchicalLabels:
        label_info = {
            'text': label.text,
            'shape': label.shape,  # input/output/bidirectional/etc
            'position': (label.position.X, label.position.Y),
            'angle': label.position.angle
        }
        labels['hierarchical'].append(label_info)
    
    # Parse power symbols (they appear as schematic symbols)
    for symbol in schematic.schematicSymbols:
        if symbol.libraryNickname == 'power':
            if hasattr(symbol, 'properties'):
                # Find the Value property which contains the power net name
                value_prop = next((prop for prop in symbol.properties if prop.key == 'Value'), None)
                if value_prop:
                    label_info = {
                        'text': value_prop.value,
                        'position': (symbol.position.X, symbol.position.Y),
                        'angle': symbol.position.angle
                    }
                    labels['power'].append(label_info)

    return labels

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

def get_wire_connections(schematic):
    """
    Extract wire connections from the schematic
    """
    wire_connections = []
    
    for item in schematic.graphicalItems:
        if hasattr(item, 'type') and item.type == 'wire':
            start_point = (float(item.points[0].X), float(item.points[0].Y))
            end_point = (float(item.points[1].X), float(item.points[1].Y))
            wire_connections.append((start_point, end_point))
    
    return wire_connections

def find_label_for_position(position, labels, wire_connections, tolerance=0.01):
    """
    Find a label that connects to the given position, either directly or through wires
    """
    # Helper function to check if points are close enough to be considered connected
    def points_match(p1, p2, tolerance=0.01):
        return (abs(p1[0] - p2[0]) <= tolerance and 
                abs(p1[1] - p2[1]) <= tolerance)
    
    # Helper function to get all connected points through wires
    def get_connected_points(start_pos, wire_list, visited=None):
        if visited is None:
            visited = set()
        
        connected_points = {start_pos}
        for wire in wire_list:
            wire_start = (wire[0][0], wire[0][1])
            wire_end = (wire[1][0], wire[1][1])
            
            if (wire_start, wire_end) in visited:
                continue
                
            visited.add((wire_start, wire_end))
            
            if points_match(start_pos, wire_start, tolerance):
                connected_points.add(wire_end)
                connected_points.update(
                    get_connected_points(wire_end, wire_list, visited)
                )
            elif points_match(start_pos, wire_end, tolerance):
                connected_points.add(wire_start)
                connected_points.update(
                    get_connected_points(wire_start, wire_list, visited)
                )
                
        return connected_points

    # Get all points connected to the given position
    connected_points = get_connected_points(position, wire_connections)
    
    # Check local labels
    for label in labels['local']:
        label_pos = (label['position'][0], label['position'][1])
        if any(points_match(label_pos, p, tolerance) for p in connected_points):
            return ('local', label['text'])
            
    # Check hierarchical labels
    for label in labels['hierarchical']:
        label_pos = (label['position'][0], label['position'][1])
        if any(points_match(label_pos, p, tolerance) for p in connected_points):
            return ('hierarchical', label['text'])
            
    # Check power labels
    for label in labels['power']:
        label_pos = (label['position'][0], label['position'][1])
        if any(points_match(label_pos, p, tolerance) for p in connected_points):
            return ('power', label['text'])
            
    return None

def calculate_pin_connectivity(component_pins, wire_connections, labels):
    """
    Calculate connectivity between pins and labels, properly handling local labels
    """
    netlist = {}
    net_counter = 1
    
    def are_points_connected(point1, point2, wire_list, local_labels, visited=None):
        if visited is None:
            visited = set()
            
        p1 = (round(point1[0], 2), round(point1[1], 2))
        p2 = (round(point2[0], 2), round(point2[1], 2))
        
        if p1 == p2:
            return True
        
        # Check if points share a local label
        label1 = find_label_for_position(p1, labels, wire_list)
        label2 = find_label_for_position(p2, labels, wire_list)
        
        if label1 and label2 and label1[1] == label2[1] and label1[0] == 'local':
            return True
            
        for wire in wire_list:
            wire_start = (round(wire[0][0], 2), round(wire[0][1], 2))
            wire_end = (round(wire[1][0], 2), round(wire[1][1], 2))
            
            wire_key = (wire_start, wire_end)
            if wire_key in visited:
                continue
                
            if p1 in (wire_start, wire_end):
                visited.add(wire_key)
                other_point = wire_end if p1 == wire_start else wire_start
                if are_points_connected(other_point, p2, wire_list, local_labels, visited):
                    return True
                    
        return False

    # Process pins and assign to nets
    unassigned_pins = []
    for component, pins in component_pins.items():
        for pin in pins:
            pin_position = pin['absolute_position']
            pin_info = {
                'component': component,
                'pin_number': pin['pin_number'],
                'pin_name': pin['pin_name'],
                'position': pin_position
            }
            unassigned_pins.append(pin_info)
    
    # Group pins into nets, including local label connections
    while unassigned_pins:
        current_pin = unassigned_pins.pop(0)
        current_net = [current_pin]
        
        # Check connectivity with remaining pins
        i = 0
        while i < len(unassigned_pins):
            test_pin = unassigned_pins[i]
            if are_points_connected(
                current_pin['position'],
                test_pin['position'],
                wire_connections,
                labels['local']
            ):
                current_net.append(test_pin)
                unassigned_pins.pop(i)
            else:
                i += 1
        
        # Look for a label connected to any pin in this net
        net_name = None
        for pin in current_net:
            label_info = find_label_for_position(
                pin['position'],
                labels,
                wire_connections
            )
            if label_info:
                label_type, label_text = label_info
                # Prioritize local labels
                if label_type == 'local':
                    net_name = label_text
                    break
                elif not net_name:  # Use other label types as fallback
                    net_name = label_text
                
        if net_name is None:
            net_name = f"NET_{net_counter}"
            net_counter += 1
            
        netlist[net_name] = current_net
    
    return netlist
def analyze_schematic(schematic):
    """
    Analyze schematic and print component pin positions, connectivity, and labels
    """
    # Get component pins
    component_pins = get_component_pins(schematic)
    
    # Get wire connections
    wire_connections = get_wire_connections(schematic)
    
    # Parse labels
    labels = parse_labels(schematic)
    
    # Calculate pin connectivity with label-based net names
    netlist = calculate_pin_connectivity(component_pins, wire_connections, labels)
    
    # Print results
    print("\n=== Component Pin Positions ===")
    for component_ref, pins in component_pins.items():
        print(f"\nComponent: {component_ref}")
        for pin in pins:
            print(f"  Pin {pin['pin_number']} ({pin['pin_name']}):")
            print(f"    Position: ({pin['absolute_position'][0]:.2f}, "
                  f"{pin['absolute_position'][1]:.2f})")
            print(f"    Type: {pin['electrical_type']}")
    
    print("\n=== Labels ===")
    print("\nLocal Labels:")
    for label in labels['local']:
        print(f"  {label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nHierarchical Labels:")
    for label in labels['hierarchical']:
        print(f"  {label['text']} ({label['shape']}) at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nPower Labels:")
    for label in labels['power']:
        print(f"  {label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
    
    print("\n=== Netlist ===")
    for net_name, connected_pins in netlist.items():
        print(f"\n{net_name}:")
        for pin in connected_pins:
            print(f"  {pin['component']} Pin {pin['pin_number']} ({pin['pin_name']})")


from kiutils.schematic import Schematic
import math
import sys
import os

def parse_labels(schematic):
    """
    Parse different types of labels from the schematic
    """
    labels = {
        'local': [],
        'hierarchical': [],
        'power': []
    }
    
    # Parse local labels
    for label in schematic.labels:
        labels['local'].append({
            'text': label.text,
            'position': (label.position.X, label.position.Y),
            'angle': label.position.angle
        })
        
    # Parse hierarchical labels
    for label in schematic.hierarchicalLabels:
        labels['hierarchical'].append({
            'text': label.text,
            'shape': label.shape,  # input/output/bidirectional/etc
            'position': (label.position.X, label.position.Y),
            'angle': label.position.angle
        })
    
    # Parse power symbols
    for symbol in schematic.schematicSymbols:
        if symbol.libraryNickname == 'power':
            value_prop = next((prop for prop in symbol.properties if prop.key == 'Value'), None)
            if value_prop:
                labels['power'].append({
                    'text': value_prop.value,
                    'position': (symbol.position.X, symbol.position.Y),
                    'angle': symbol.position.angle
                })

    return labels

def parse_hierarchical_sheets(schematic, base_path):
    """
    Recursively parse hierarchical sheets and merge results into the main schematic.
    """
    all_schematics = [schematic]

    for sheet in schematic.sheets:
        sheet_file = next((prop.value for prop in sheet.properties if prop.key == "Sheetfile"), None)
        if sheet_file:
            child_path = os.path.join(base_path, sheet_file)
            try:
                child_schematic = Schematic().from_file(child_path)
                all_schematics.extend(parse_hierarchical_sheets(child_schematic, os.path.dirname(child_path)))
            except FileNotFoundError:
                print(f"Error: Unable to find hierarchical sheet file: {child_path}")

    return all_schematics

def analyze_schematic(schematic, base_path):
    """
    Analyze schematic and generate comprehensive information about components, pins, and connectivity.
    """
    # Parse all schematics, including hierarchical ones
    all_schematics = parse_hierarchical_sheets(schematic, base_path)

    # Merge data across all schematics
    all_labels = {'local': [], 'hierarchical': [], 'power': []}
    all_wire_connections = []
    all_component_pins = {}

    for sch in all_schematics:
        labels = parse_labels(sch)
        all_labels['local'].extend(labels['local'])
        all_labels['hierarchical'].extend(labels['hierarchical'])
        all_labels['power'].extend(labels['power'])

        all_wire_connections.extend(get_wire_connections(sch))

        component_pins = get_component_pins(sch)
        all_component_pins.update(component_pins)

    # Generate netlist
    netlist = calculate_pin_connectivity(all_component_pins, all_wire_connections, all_labels)

    # Print component information
    print("\n=== Components ===")
    for symbol in schematic.schematicSymbols:
        if symbol.libraryNickname != 'power':  # Skip power symbols as they're handled separately
            print(f"\nComponent: {symbol.libraryNickname}/{symbol.entryName}")
            print("Properties:")
            for prop in symbol.properties:
                print(f"  {prop.key}: {prop.value}")
            print(f"Position: ({symbol.position.X}, {symbol.position.Y}), Angle: {symbol.position.angle}")
            
            # Print unit information if available
            if hasattr(symbol, 'unit'):
                print(f"Unit: {symbol.unit}")

    # Print pin information with more details
    print("\n=== Pin Details ===")
    for component, pins in all_component_pins.items():
        print(f"\nComponent: {component}")
        for pin in pins:
            print(f"\n  Pin {pin['pin_number']} ({pin['pin_name']}):")
            print(f"    Position: ({pin['absolute_position'][0]:.2f}, {pin['absolute_position'][1]:.2f})")
            print(f"    Type: {pin['electrical_type']}")
            if 'alternatePins' in pin:
                print("    Alternate Functions:")
                for alt in pin['alternatePins']:
                    print(f"      - {alt['pinName']} ({alt['electricalType']})")

    # Print graphical items
    print("\n=== Graphical Items ===")
    for item in schematic.graphicalItems:
        if hasattr(item, 'type'):
            print(f"\nType: {item.type}")
            if item.type == 'wire':
                print(f"  Start: ({item.points[0].X}, {item.points[0].Y})")
                print(f"  End: ({item.points[1].X}, {item.points[1].Y})")

    # Print labels
    print("\n=== Labels ===")
    print("\nLocal Labels:")
    for label in all_labels['local']:
        print(f"  {label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nHierarchical Labels:")
    for label in all_labels['hierarchical']:
        print(f"  {label['text']} ({label['shape']}) at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")
        
    print("\nPower Labels:")
    for label in all_labels['power']:
        print(f"  {label['text']} at ({label['position'][0]:.2f}, {label['position'][1]:.2f})")

    # Print netlist
    print("\n=== Netlist ===")
    for net_name, connected_pins in netlist.items():
        print(f"\n{net_name}:")
        for pin in connected_pins:
            print(f"  {pin['component']} Pin {pin['pin_number']} ({pin['pin_name']})")

def main(file_path):
    # Load the schematic
    base_path = os.path.dirname(file_path)
    schematic = Schematic().from_file(file_path)
    print(f"Loaded schematic: {schematic}")

    # Analyze the schematic
    analyze_schematic(schematic, base_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kiutils_test.py <schematic_file_path>")
    else:
        main(sys.argv[1])
