from .wire_parser import get_connected_points
from ..labels.label_parser import parse_labels
from ..utils.geometry import points_match

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
