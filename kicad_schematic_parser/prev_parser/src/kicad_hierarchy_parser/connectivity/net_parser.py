from .wire_parser import get_connected_points
from ..labels.label_parser import parse_labels
from ..utils.geometry import points_match

def find_labels_for_position(position, labels, wire_connections, tolerance=0.01):
    """
    Enhanced label detection that checks all physically connected points
    """
    # print(f"\nFinding labels for position {position}")
    def get_all_connected_points(point, visited=None):
        """Helper function to get all points connected to a point"""
        if visited is None:
            visited = set()
            
        result = set()
        to_visit = {point}
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
                
            visited.add(current)
            result.add(current)
            
            # Get points connected to this point
            connected = get_connected_points(current, wire_connections)
            result.update(connected)
            
            # Add new points to visit
            for conn_point in connected:
                if conn_point not in visited:
                    to_visit.add(conn_point)
                    # Also add points connected to this point
                    conn_points = get_connected_points(conn_point, wire_connections)
                    to_visit.update(p for p in conn_points if p not in visited)
            
        return result
    
    # Get all physically connected points
    connected_points = get_all_connected_points(position)
    
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
                
    # print(f"Found labels: {found_labels}")
    return list(set(found_labels))  # Remove duplicates

def create_initial_nets(component_pins, wire_connections, labels):
    """
    Create initial nets with improved connection tracking, including sheet pins
    """
    # Add sheet pins as special "components"
    for label in labels['hierarchical']:
        if 'uuid' in label:  # This indicates it's a sheet pin
            pin_info = {
                'pin_number': '1',  # Sheet pins don't have numbers
                'pin_name': label['text'],
                'absolute_position': label['position'],
                'electrical_type': label['shape']  # Sheet pins store type as 'shape' (input/output)
            }
            component_name = f"Sheet_{label['sheet_name']}"
            if component_name not in component_pins:
                component_pins[component_name] = []
            component_pins[component_name].append(pin_info)
    def get_all_connected_points(point, visited=None):
        """Helper function to get all points connected to a point"""
        if visited is None:
            visited = set()
            
        result = set()
        to_visit = {point}
        
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
                
            visited.add(current)
            result.add(current)
            
            # Get points connected to this point
            connected = get_connected_points(current, wire_connections)
            result.update(connected)
            
            # Add new points to visit
            for conn_point in connected:
                if conn_point not in visited:
                    to_visit.add(conn_point)
                    # Also add points connected to this point
                    conn_points = get_connected_points(conn_point, wire_connections)
                    to_visit.update(p for p in conn_points if p not in visited)
            
        return result
    
    net_groups = {}
    next_id = 1
    point_to_net = {}  # Map points to their assigned net ID
    
    # First pass: Create nets for physically connected points
    for component, pins in component_pins.items():
        for pin in pins:
            pin_pos = pin['absolute_position']
            pin_pos_key = (round(pin_pos[0], 4), round(pin_pos[1], 4))
            
            # Get all physically connected points
            connected_points = get_all_connected_points(pin_pos)
            connected_point_keys = {(round(p[0], 4), round(p[1], 4)) for p in connected_points}
            
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

def merge_connected_nets(net_groups, wire_connections, labels):
    """
    Enhanced net merging with improved label handling and recursive connection search
    """
    def get_all_connected_points(points, visited=None):
        """Helper function to get all points connected to a set of points"""
        if visited is None:
            visited = set()
            
        result = set()
        to_visit = set(points)
        
        while to_visit:
            point = to_visit.pop()
            if point in visited:
                continue
                
            visited.add(point)
            result.add(point)
            
            # Get points connected to this point
            connected = get_connected_points(point, wire_connections)
            result.update(connected)
            
            # Add new points to visit
            for conn_point in connected:
                if conn_point not in visited:
                    to_visit.add(conn_point)
                    # Also add points connected to this point
                    conn_points = get_connected_points(conn_point, wire_connections)
                    to_visit.update(p for p in conn_points if p not in visited)
            
        return result
    
    def get_connected_nets(net_id, processed=None, visited_points=None):
        """Find all nets connected to the given net"""
        if processed is None:
            processed = set()
        if visited_points is None:
            visited_points = set()
            
        if net_id in processed:
            return set()
            
        connected = {net_id}
        processed.add(net_id)
        
        net_info = net_groups[net_id]
        
        # Get all physically connected points
        net_points = get_all_connected_points(net_info['connected_points'])
        visited_points.update(net_points)
        
        # Check which nets share any of these points
        for other_id, other_info in net_groups.items():
            if other_id in processed:
                continue
                
            # Get all points connected to the other net
            other_points = get_all_connected_points(other_info['connected_points'])
            
            # Check if any points overlap or are connected by wires
            connected_found = False
            for point1 in net_points:
                if connected_found:
                    break
                connected_points = get_connected_points(point1, wire_connections)
                for point2 in other_points:
                    if point2 in connected_points:
                        connected.update(get_connected_nets(other_id, processed, visited_points))
                        connected_found = True
                        break
                        
            # Check if any points are connected through labels
            if not connected_found:
                # Get all labels for this net's points
                net_labels = set()
                for point in net_points:
                    point_labels = find_labels_for_position(point, labels, wire_connections)
                    net_labels.update(point_labels)
                
                # Get all labels for other net's points
                other_labels = set()
                for point in other_points:
                    point_labels = find_labels_for_position(point, labels, wire_connections)
                    other_labels.update(point_labels)
                
                # Check if any labels match
                for label1 in net_labels:
                    for label2 in other_labels:
                        # Direct match - same type and name
                        if label1[0] == label2[0] and label1[1] == label2[1]:
                            connected.update(get_connected_nets(other_id, processed, visited_points))
                            connected_found = True
                            break
                    if connected_found:
                        break
                
        return connected
    
    # Create merged nets from groups
    merged_nets = {}
    processed = set()
    
    for net_id in net_groups:
        if net_id in processed:
            continue
            
        # Find all connected nets
        group = get_connected_nets(net_id)
        if group:
            # Create merged net
            merged_id = f"MERGED_NET_{len(merged_nets) + 1}"
            merged_net = {
                'pins': [],
                'labels': [],
                'connected_points': set()
            }
            
            # Merge all information from grouped nets
            for gid in group:
                net_info = net_groups[gid]
                merged_net['pins'].extend(net_info['pins'])
                merged_net['labels'].extend(net_info['labels'])
                merged_net['connected_points'].update(net_info['connected_points'])
                processed.add(gid)
                
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
    
    # Merge connected nets with wire_connections for physical connectivity check
    merged_nets = merge_connected_nets(initial_nets, wire_connections, labels)
    
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
        
        # Prefer hierarchical labels from sheet pins first, then other labels
        net_name = net_id
        
        # Check for hierarchical labels from sheet pins
        sheet_labels = [l[1] for l in net_info['labels']
                      if l[0] == 'hierarchical' and l[1].startswith("Sheet_")]
        if sheet_labels:
            net_name = sheet_labels[0]
        elif hier_labels:
            net_name = hier_labels[0]
        elif power_labels:
            net_name = power_labels[0]
        elif local_labels:
            net_name = local_labels[0]
            
        # Skip empty nets
        if not net_info['pins'] and not power_labels and not hier_labels and not local_labels:
            continue
        
        # Create netlist entry
        netlist[net_name] = {
            'pins': [],
            'power_labels': power_labels,
            'hierarchical_labels': hier_labels,
            'local_labels': local_labels
        }
        
        # Add all pins that are physically connected
        for comp, pin in net_info['pins']:
            pin_pos = pin['absolute_position']
            connected_points = get_connected_points(pin_pos, wire_connections)
            
            # Add pin if it's connected to any point in this net
            if connected_points.intersection(net_info['connected_points']):
                netlist[net_name]['pins'].append({
                    'component': comp,
                    'pin_number': pin['pin_number'],
                    'pin_name': pin['pin_name']
                })
    
    return netlist
