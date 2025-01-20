import os
from .wire_parser import get_connected_points
from ..labels.label_parser import parse_labels
from ..utils.geometry import points_match
from kiutils.schematic import Schematic

def build_sheet_hierarchy(schematic, base_path):
    """Build tree of sheet relationships"""
    hierarchy = {'root': {'path': base_path, 'pins': []}}
    
    def process_sheet(schematic, parent_path):
        for sheet in schematic.sheets:
            sheet_name = sheet.sheetName.value
            sheet_file = sheet.fileName.value
            sheet_path = os.path.join(base_path, sheet_file)
            
            # Safely handle pins, ensuring it's always a list
            sheet_pins = []
            if hasattr(sheet, 'pins'):
                # Ensure pins is a list, even if it's a single item or None
                if sheet.pins is not None:
                    sheet_pins = sheet.pins if isinstance(sheet.pins, list) else [sheet.pins]
            
            # Store sheet info including pins
            hierarchy[sheet_name] = {
                'path': sheet_path,
                'parent': parent_path,
                'pins': [
                    {
                        'name': pin.name if hasattr(pin, 'name') else str(pin),
                        'type': pin.connectionType if hasattr(pin, 'connectionType') else 'unknown',
                        'uuid': pin.uuid if hasattr(pin, 'uuid') else None
                    }
                    for pin in sheet_pins
                ]
            }
            
            # Process child sheet
            try:
                child_schematic = Schematic().from_file(sheet_path)
                process_sheet(child_schematic, sheet_path)
            except Exception as e:
                print(f"Warning: Could not process sheet {sheet_name}: {e}")
                
    process_sheet(schematic, base_path)
    return hierarchy

def find_labels_for_position(position, labels, wire_connections, tolerance=0.01):
    """
    Enhanced label detection that checks all physically connected points
    """
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
                
    return list(set(found_labels))  # Remove duplicates

def create_initial_nets(component_pins, wire_connections, labels):
    """
    Create initial nets with improved connection tracking, including sheet pins
    """

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

    net_groups = {}
    next_id = 1
    point_to_net = {}  # Map points to their assigned net ID
    
    # First pass: Create nets for physically connected points
    for component, pins in component_pins.items():
        for pin in pins:
            pin_pos = pin['absolute_position']
            pin_pos_key = (round(pin_pos[0], 2), round(pin_pos[1], 2))
            
            # Get all physically connected points
            connected_points = get_all_connected_points(pin_pos)
            connected_point_keys = {(round(p[0], 2), round(p[1], 2)) for p in connected_points}
            
            # Find if any points are already assigned to a net
            existing_nets = set()
            for point_key in connected_point_keys:
                if point_key in point_to_net:
                    existing_nets.add(point_to_net[point_key])
            
            # If connected to existing net(s), merge into the first one
            if existing_nets:
                target_net_id = min(existing_nets)
                # Include component sheet info
                sheet_name = component.split('/')[-2] if '/' in component else 'root'
                pin_info = {
                    'component': component,
                    'pin': pin,
                    'sheet': sheet_name
                }
                net_groups[target_net_id]['pins'].append(pin_info)
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

    def get_connected_nets(net_id, processed=None, visited_points=None, recursion_depth=0):
        """Find all nets connected to the given net"""
        # Add recursion depth limit
        MAX_RECURSION_DEPTH = 50
        if recursion_depth > MAX_RECURSION_DEPTH:
            return set()
            
        if processed is None:
            processed = set()
        if visited_points is None:
            visited_points = set()
            
        if net_id in processed:
            return set()
            
        connected = {net_id}
        processed.add(net_id)
        
        try:
            net_info = net_groups[net_id]
        except KeyError:
            print(f"Warning: Net {net_id} not found in net_groups")
            return connected
            
        # Get points for this net that haven't been visited
        net_points = set(net_info['connected_points']) - visited_points
        visited_points.update(net_points)
        
        # Early exit if no new points to process
        if not net_points:
            return connected
        
        # Check which nets share any of these points
        for other_id, other_info in net_groups.items():
            if other_id in processed:
                continue
                
            # Get unvisited points from other net
            other_points = set(other_info['connected_points']) - visited_points
            
            # Check if any points overlap
            if net_points & other_points:
                connected.update(
                    get_connected_nets(other_id, processed, visited_points, recursion_depth + 1)
                )
                
        return connected
    
    """Enhanced net merging with improved label handling"""
    merged_nets = {}
    processed = set()
    max_iterations = len(net_groups) * 2  # Reasonable upper limit
    iteration = 0
    
    for net_id in net_groups:
        if net_id in processed:
            continue
            
        if iteration > max_iterations:
            print("Warning: Maximum merge iterations reached")
            break
            
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
                if gid in net_groups:  # Add safety check
                    net_info = net_groups[gid]
                    merged_net['pins'].extend(net_info['pins'])
                    merged_net['labels'].extend(net_info['labels'])
                    merged_net['connected_points'].update(net_info['connected_points'])
                    processed.add(gid)
                    
            # Remove duplicates
            merged_net['labels'] = list(set(merged_net['labels']))
            merged_nets[merged_id] = merged_net
            
        iteration += 1
            
    return merged_nets

def calculate_pin_connectivity(component_pins, wire_connections, labels, sheet_hierarchy=None):
    """Calculate connectivity between pins and labels with improved handling of multiple connections
    
    Args:
        component_pins: Dict of component pins
        wire_connections: List of wire connections
        labels: Dict of labels by type
        sheet_hierarchy: Optional sheet hierarchy information
    
    Returns:
        dict: Calculated netlist
    """
    # Create initial nets from physical connections
    initial_nets = create_initial_nets(component_pins, wire_connections, labels)
    
    # Merge connected nets with wire_connections for physical connectivity check
    merged_nets = merge_connected_nets(initial_nets, wire_connections, labels)
    
    # If we have sheet hierarchy information, merge across hierarchies
    if sheet_hierarchy:
        merged_nets = merge_hierarchical_nets(merged_nets, sheet_hierarchy)
    
    return merged_nets

def merge_hierarchical_nets(netlists, sheet_hierarchy):
    """Merge nets across hierarchical boundaries"""
    global_netlist = {}
    for sheet_name, sheet_netlist in netlists.items():
        for net_name, net_info in sheet_netlist.items():
            if net_name.startswith('+') or net_name == 'GND':
                if net_name not in global_netlist:
                    global_netlist[net_name] = {
                        'pins': [],
                        'labels': [],
                        'sheets': set()
                    }
                # Handle case where net_info is list or dict
                if isinstance(net_info, dict):
                    for pin_info in net_info.get('pins', []):
                        pin_info['sheet'] = sheet_name
                        global_netlist[net_name]['pins'].append(pin_info)
                    global_netlist[net_name]['labels'].extend(net_info.get('labels', []))
                    global_netlist[net_name]['sheets'].add(sheet_name)
    # First collect power nets (these are global)
    for net_name, net_info in netlists.items():
        if net_name.startswith('+') or net_name == 'GND':
            if net_name not in global_netlist:
                global_netlist[net_name] = {
                    'pins': [],
                    'labels': [],
                    'sheets': set()
                }
            # Handle case where labels and pins are lists
            if isinstance(net_info, dict):
                global_netlist[net_name]['pins'].extend(net_info.get('pins', []))
                global_netlist[net_name]['labels'].extend(net_info.get('labels', []))
            elif isinstance(net_info, list):
                # If net_info is a list, assume it's list of pins
                global_netlist[net_name]['pins'].extend(net_info)
            
    # Build map of hierarchical labels to sheet pins
    hier_connections = {}
    for sheet_name, sheet_info in sheet_hierarchy.items():
        if 'pins' in sheet_info:
            for pin in sheet_info['pins']:
                pin_name = pin['name']
                # Map sheet pin to its hierarchical label
                hier_connections[f"{sheet_name}/{pin_name}"] = pin_name
                
    # Connect nets through hierarchical boundaries
    for sheet_name, sheet_netlist in netlists.items():
        for net_name, net_info in sheet_netlist.items():
            # Skip already processed power nets
            if net_name.startswith('+') or net_name == 'GND':
                continue
                
            # Look for hierarchical labels
            hier_labels = []
            if isinstance(net_info, dict) and 'labels' in net_info:
                for label in net_info['labels']:
                    if isinstance(label, tuple) and len(label) > 1 and label[0] == 'hierarchical':
                        hier_labels.append(label[1])
            elif isinstance(net_info, list):
                # If net_info is a list, check each item for hierarchical labels
                for item in net_info:
                    if isinstance(item, tuple) and len(item) > 1 and item[0] == 'hierarchical':
                        hier_labels.append(item[1])
                    
            # Create merged name for this net
            merged_name = f"{sheet_name}/{net_name}"
            
            # If net has hierarchical labels, merge with connected nets
            if hier_labels:
                if merged_name not in global_netlist:
                    global_netlist[merged_name] = {
                        'pins': [],
                        'labels': [],
                        'sheets': set([sheet_name])
                    }
                
            # Add this net's components and labels if it exists in global_netlist
            if merged_name in global_netlist:
                if isinstance(net_info, dict):
                    global_netlist[merged_name]['pins'].extend(net_info.get('pins', []))
                    global_netlist[merged_name]['labels'].extend(net_info.get('labels', []))
                elif isinstance(net_info, (list, tuple)):
                    # Extract pins and any labels from list items
                    pins = []
                    labels = []
                    for item in net_info:
                        if isinstance(item, dict):
                            pins.append(item)
                        elif isinstance(item, tuple) and len(item) > 1:
                            if item[0] == 'label':
                                labels.append(item[1])
                    global_netlist[merged_name]['pins'].extend(pins)
                    global_netlist[merged_name]['labels'].extend(labels)
                
                # Look for matching sheet pins
                for label in hier_labels:
                    sheet_pin_key = f"{sheet_name}/{label}"
                    if sheet_pin_key in hier_connections:
                        connected_label = hier_connections[sheet_pin_key]
                        # Find and merge other nets with this label
                        for other_sheet, other_netlist in netlists.items():
                            if other_sheet == sheet_name:
                                continue
                            for other_net, other_info in other_netlist.items():
                                if isinstance(other_info, dict):
                                    other_labels = other_info.get('labels', [])
                                else:  # list case
                                    other_labels = [item for item in other_info if isinstance(item, tuple)]
                                    
                                if any(l[1] == connected_label for l in other_labels if isinstance(l, tuple) and len(l) > 1):
                                    other_name = f"{other_sheet}/{other_net}"
                                    if other_name not in global_netlist:
                                        # Handle different net_info types when creating new entry
                                        pins = []
                                        labels = []
                                        if isinstance(other_info, dict):
                                            pins = other_info.get('pins', [])
                                            labels = other_info.get('labels', [])
                                        elif isinstance(other_info, (list, tuple)):
                                            for item in other_info:
                                                if isinstance(item, dict):
                                                    pins.append(item)
                                                elif isinstance(item, tuple) and len(item) > 1:
                                                    if item[0] == 'label':
                                                        labels.append(item[1])
                                        
                                        global_netlist[other_name] = {
                                            'pins': pins,
                                            'labels': labels,
                                            'sheets': set([other_sheet])
                                        }
                                    # Merge the nets
                                    global_netlist[merged_name]['pins'].extend(global_netlist[other_name]['pins'])
                                    global_netlist[merged_name]['labels'].extend(global_netlist[other_name]['labels'])
                                    global_netlist[merged_name]['sheets'].add(other_sheet)

    return global_netlist
