from kiutils.schematic import Schematic
import math
import sys


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


def find_labels_for_position(position, labels, wire_connections, tolerance=0.01):
    """
    Enhanced label detection that checks all physically connected points
    """
    # Get all physically connected points
    connected_points = get_connected_points(position, wire_connections, tolerance=tolerance)
    
    found_labels = []
    
    # Check each connected point against all label types
    for point in connected_points:
        # Check power labels
        for label in labels['power']:
            if points_match(point, label['position'], tolerance):
                found_labels.append(('power', label['text']))
                
        # Check hierarchical labels  
        for label in labels['hierarchical']:
            if points_match(point, label['position'], tolerance):
                found_labels.append(('hierarchical', label['text']))
                
        # Check local labels
        for label in labels['local']:
            if points_match(point, label['position'], tolerance):
                found_labels.append(('local', label['text']))
                
    return list(set(found_labels))  # Remove duplicates


def are_points_connected(point1, point2, wire_connections, labels, tolerance=0.01):
    """
    Check if two points are connected either directly through wires or through shared labels.
    
    Args:
        point1: First point (x,y) tuple
        point2: Second point (x,y) tuple  
        wire_connections: List of wire connections
        labels: Dictionary of label information
        tolerance: Distance tolerance for point matching

    Returns:
        bool: True if points are connected, False otherwise
    """
    def points_match(p1, p2, tolerance=0.01):
        return (abs(p1[0] - p2[0]) <= tolerance and 
                abs(p1[1] - p2[1]) <= tolerance)
            
    def get_connected_points(start_pos, wire_list, visited=None, tolerance=0.01):
        """
        Find all points connected to start_pos through wires, recursively
        
        Args:
            start_pos: Starting point (x,y) tuple
            wire_list: List of wire connections
            visited: Set of already visited wire segments
            tolerance: Distance tolerance for point matching
            
        Returns:
            set: Set of all connected points
        """
        if visited is None:
            visited = set()
            
        # Convert point coordinates to 2-decimal precision for reliable matching
        start_pos = (round(start_pos[0], 2), round(start_pos[1], 2))
        connected_points = {start_pos}
        
        for wire in wire_list:
            wire_start = (round(wire[0][0], 2), round(wire[0][1], 2))
            wire_end = (round(wire[1][0], 2), round(wire[1][1], 2))
            
            wire_key = (wire_start, wire_end)
            if wire_key in visited:
                continue
                
            visited.add(wire_key)
            visited.add((wire_end, wire_start))  # Add both orientations
            
            # Check if this wire connects to our point
            if points_match(start_pos, wire_start, tolerance):
                connected_points.add(wire_end)
                connected_points.update(
                    get_connected_points(wire_end, wire_list, visited, tolerance)
                )
            elif points_match(start_pos, wire_end, tolerance):
                connected_points.add(wire_start)
                connected_points.update(
                    get_connected_points(wire_start, wire_list, visited, tolerance)
                )
                    
        return connected_points



    # Get all points connected to point1 and point2 through wires
    p1_connected = get_connected_points(point1, wire_connections)
    p2_connected = get_connected_points(point2, wire_connections)
    
    # Direct wire connection check
    if any(points_match(p1, p2, tolerance) for p1 in p1_connected for p2 in p2_connected):
        return True
        
    # Check connection through labels
    p1_labels = find_labels_for_position(point1, labels, wire_connections)
    p2_labels = find_labels_for_position(point2, labels, wire_connections)
    
    # Check for shared label connections
    for label1 in p1_labels:
        for label2 in p2_labels:
            # If both points connect to the same label name, they're connected
            if label1[1] == label2[1]:
                return True
                
    return False


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

def points_match(p1, p2, tolerance=0.01):
    """Helper function to check if two points match within tolerance"""
    return (abs(p1[0] - p2[0]) <= tolerance and 
            abs(p1[1] - p2[1]) <= tolerance)


def get_connected_points(start_pos, wire_list, visited=None, tolerance=0.01):
    """
    Find all points connected to start_pos through wires, recursively
    
    Args:
        start_pos: Starting point (x,y) tuple
        wire_list: List of wire connections
        visited: Set of already visited wire segments
        tolerance: Distance tolerance for point matching
        
    Returns:
        set: Set of all connected points
    """
    if visited is None:
        visited = set()
        
    # Convert point coordinates to 2-decimal precision for reliable matching
    start_pos = (round(start_pos[0], 2), round(start_pos[1], 2))
    connected_points = {start_pos}
    
    for wire in wire_list:
        wire_start = (round(wire[0][0], 2), round(wire[0][1], 2))
        wire_end = (round(wire[1][0], 2), round(wire[1][1], 2))
        
        wire_key = (wire_start, wire_end)
        if wire_key in visited:
            continue
            
        visited.add(wire_key)
        visited.add((wire_end, wire_start))  # Add both orientations
        
        # Check if this wire connects to our point
        if points_match(start_pos, wire_start, tolerance):
            connected_points.add(wire_end)
            connected_points.update(
                get_connected_points(wire_end, wire_list, visited, tolerance)
            )
        elif points_match(start_pos, wire_end, tolerance):
            connected_points.add(wire_start)
            connected_points.update(
                get_connected_points(wire_start, wire_list, visited, tolerance)
            )
                
    return connected_points

def point_on_wire_segment(point, wire_start, wire_end, tolerance=0.01):
    """
    Check if a point lies on a wire segment
    """
    # Convert to 2 decimal precision for reliable comparison
    px, py = round(point[0], 2), round(point[1], 2)
    x1, y1 = round(wire_start[0], 2), round(wire_start[1], 2)
    x2, y2 = round(wire_end[0], 2), round(wire_end[1], 2)
    
    # Check if point is within the bounding box of the wire
    if not (min(x1, x2) - tolerance <= px <= max(x1, x2) + tolerance and
            min(y1, y2) - tolerance <= py <= max(y1, y2) + tolerance):
        return False
        
    # For vertical wires
    if abs(x1 - x2) < tolerance:
        return abs(px - x1) < tolerance
        
    # For horizontal wires
    if abs(y1 - y2) < tolerance:
        return abs(py - y1) < tolerance
        
    # For diagonal wires (if any)
    # Calculate distance from point to line
    numerator = abs((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1)
    denominator = ((y2-y1)**2 + (x2-x1)**2)**0.5
    distance = numerator/denominator
    
    return distance < tolerance


def create_initial_nets(component_pins, wire_connections, labels):
    """
    Create initial nets with improved connection tracking
    """
    net_groups = {}
    next_id = 1
    point_to_net = {}  # Map points to their assigned net ID
    
    # First pass: Create nets for physically connected points
    for component, pins in component_pins.items():
        for pin in pins:
            pin_pos = pin['absolute_position']
            pin_pos_key = (round(pin_pos[0], 2), round(pin_pos[1], 2))
            
            # Get all physically connected points
            connected_points = get_connected_points(pin_pos, wire_connections)
            connected_point_keys = {(round(p[0], 2), round(p[1], 2)) for p in connected_points}
            
            # Find if any points are already assigned to a net
            existing_nets = set()
            for point_key in connected_point_keys:
                if point_key in point_to_net:
                    existing_nets.add(point_to_net[point_key])
            
            # If connected to existing net(s), merge into the first one
            if existing_nets:
                target_net_id = min(existing_nets)  # Use the lowest net ID
                net_groups[target_net_id]['pins'].append((component, pin))
                net_groups[target_net_id]['connected_points'].update(connected_points)
                
                # Update point mappings
                for point_key in connected_point_keys:
                    point_to_net[point_key] = target_net_id
                    
                # Merge other nets if multiple exist
                for other_net_id in existing_nets:
                    if other_net_id != target_net_id:
                        net_groups[target_net_id]['pins'].extend(net_groups[other_net_id]['pins'])
                        net_groups[target_net_id]['connected_points'].update(
                            net_groups[other_net_id]['connected_points'])
                        del net_groups[other_net_id]
            else:
                # Create new net
                net_id = f"NET_{next_id}"
                next_id += 1
                
                net_groups[net_id] = {
                    'pins': [(component, pin)],
                    'labels': [],
                    'connected_points': connected_points
                }
                
                # Map all points to this net
                for point_key in connected_point_keys:
                    point_to_net[point_key] = net_id
    
    # Second pass: Add label information
    for net_id, net_info in net_groups.items():
        # Find labels connected to any point in this net
        all_labels = []
        for point in net_info['connected_points']:
            point_labels = find_labels_for_position(point, labels, wire_connections)
            all_labels.extend(point_labels)
        net_info['labels'] = list(set(all_labels))
    
    return net_groups


def merge_connected_nets(net_groups):
    """
    Enhanced net merging with improved label handling and recursive connection search
    """
    def get_connected_nets(net_id, processed=None):
        if processed is None:
            processed = set()
            
        if net_id in processed:
            return set()
            
        connected = {net_id}
        processed.add(net_id)
        
        net_info = net_groups[net_id]
        
        # Check label connections including transitive connections
        # For example: if net1 has label1, net2 has label2, and label1 connects to label2,
        # then net1 and net2 should be connected
        net_labels = net_info['labels']
        for other_id, other_info in net_groups.items():
            if other_id in processed:
                continue
                
            other_labels = other_info['labels']
            
            # Check for direct label name matches
            for label1 in net_labels:
                for label2 in other_labels:
                    if label1[1] == label2[1]:  # Match on label name
                        connected.update(get_connected_nets(other_id, processed))
                        break
                        
        # Check point connections
        net_points = net_info['connected_points']
        for other_id, other_info in net_groups.items():
            if other_id in processed:
                continue
                
            other_points = other_info['connected_points']
            
            # Check if any points overlap
            if net_points.intersection(other_points):
                connected.update(get_connected_nets(other_id, processed))
                
        return connected

    # Build initial groups using recursive connection search
    merged_groups = []
    processed = set()
    
    for net_id in net_groups:
        if net_id in processed:
            continue
            
        group = get_connected_nets(net_id)
        if group:
            merged_groups.append(group)
            processed.update(group)

    # Create merged nets from groups
    merged_nets = {}
    for idx, group in enumerate(merged_groups, 1):
        merged_id = f"MERGED_NET_{idx}"
        merged_net = {
            'pins': [],
            'labels': [],
            'connected_points': set(),
            'source_nets': group
        }
        
        # Merge all information from grouped nets
        for net_id in group:
            net_info = net_groups[net_id]
            merged_net['pins'].extend(net_info['pins'])
            merged_net['labels'].extend(net_info['labels'])
            merged_net['connected_points'].update(net_info['connected_points'])
            
        # Remove duplicates
        merged_net['labels'] = list(set(merged_net['labels']))
        merged_nets[merged_id] = merged_net

    return merged_nets


def calculate_pin_connectivity(component_pins, wire_connections, labels):
    """
    Calculate connectivity between pins and labels with improved handling of multiple connections
    """
    # Create initial nets from physical connections
    initial_nets = create_initial_nets(component_pins, wire_connections, labels)
    
    # Merge connected nets
    merged_nets = merge_connected_nets(initial_nets)
    
    # Format the final netlist
    netlist = {}
    
    for net_id, net_info in merged_nets.items():
        # Group labels by type
        power_labels = []
        hier_labels = []
        local_labels = []
        
        for label_type, label_name in net_info['labels']:
            if label_type == 'power':
                power_labels.append(label_name)
            elif label_type == 'hierarchical':
                hier_labels.append(label_name)
            else:
                local_labels.append(label_name)
        
        # Choose primary net name based on any available label
        net_name = None
        if power_labels:
            net_name = power_labels[0]
        elif hier_labels:
            net_name = hier_labels[0]
        elif local_labels:
            net_name = local_labels[0]
        else:
            net_name = net_id
        
        # Create netlist entry
        netlist[net_name] = {
            'pins': [{'component': comp, 'pin_number': pin['pin_number'], 
                     'pin_name': pin['pin_name']} for comp, pin in net_info['pins']],
            'power_labels': power_labels,
            'hierarchical_labels': hier_labels,
            'local_labels': local_labels,
            'merged_from': list(net_info['source_nets'])
        }
    
    return netlist

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
    for net_name, net_info in netlist.items():
        print(f"\n{net_name}:")
        
        # Print connected pins
        if 'pins' in net_info:
            for pin in net_info['pins']:
                print(f"  {pin['component']} Pin {pin['pin_number']} ({pin['pin_name']})")
        
        # Print power labels
        if 'power_labels' in net_info and net_info['power_labels']:
            print("  Power Labels:")
            for label in net_info['power_labels']:
                print(f"    {label}")
                
        # Print hierarchical labels
        if 'hierarchical_labels' in net_info and net_info['hierarchical_labels']:
            print("  Hierarchical Labels:")
            for label in net_info['hierarchical_labels']:
                print(f"    {label}")
                
        # Print local labels
        if 'local_labels' in net_info and net_info['local_labels']:
            print("  Local Labels:")
            for label in net_info['local_labels']:
                print(f"    {label}")
                
        # Print merged information
        if 'merged_from' in net_info:
            print("  Merged from nets:")
            for source_net in net_info['merged_from']:
                print(f"    {source_net}")

def main(file_path):
    # Load the schematic
    base_path = os.path.dirname(file_path)
    schematic = Schematic().from_file(file_path)
    # print(f"Loaded schematic: {schematic}")

    # Analyze the schematic
    analyze_schematic(schematic, base_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kiutils_test.py <schematic_file_path>")
    else:
        main(sys.argv[1])
