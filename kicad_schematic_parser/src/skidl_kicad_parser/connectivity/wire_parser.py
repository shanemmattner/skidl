from ..utils.geometry import points_match, point_on_wire_segment

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


def get_connected_points(start_pos, wire_list, visited=None, tolerance=0.01, depth=0):
    """Find all points connected to start_pos through wires"""
    # Add maximum recursion depth
    MAX_DEPTH = 100
    if depth > MAX_DEPTH:
        return set()
        
    if not wire_list:
        return set()
        
    if visited is None:
        visited = set()
        
    # Convert point coordinates to 2-decimal precision for reliable matching
    try:
        start_pos = (round(float(start_pos[0]), 2), round(float(start_pos[1]), 2))
    except (TypeError, IndexError) as e:
        print(f"Warning: Invalid point format: {start_pos}")
        return set()
        
    # Add point itself to visited set
    point_key = start_pos
    if point_key in visited:
        return set()
    visited.add(point_key)
        
    connected_points = {start_pos}
    
    for wire in wire_list:
        try:
            wire_start = (round(float(wire[0][0]), 2), round(float(wire[0][1]), 2))
            wire_end = (round(float(wire[1][0]), 2), round(float(wire[1][1]), 2))
        except (TypeError, IndexError) as e:
            print(f"Warning: Invalid wire format: {wire}")
            continue
            
        wire_key = (wire_start, wire_end)
        if wire_key in visited:
            continue
            
        visited.add(wire_key)
        visited.add((wire_end, wire_start))  # Add both orientations
        
        # Check if this wire connects to our point
        if (points_match(start_pos, wire_start, tolerance) or 
            points_match(start_pos, wire_end, tolerance) or 
            point_on_wire_segment(start_pos, wire_start, wire_end, tolerance)):
            
            connected_points.add(wire_start)
            connected_points.add(wire_end)
            
            # Recursively find other connected points with depth tracking
            if wire_start not in visited:
                connected_points.update(
                    get_connected_points(wire_start, wire_list, visited, tolerance, depth + 1)
                )
            if wire_end not in visited:
                connected_points.update(
                    get_connected_points(wire_end, wire_list, visited, tolerance, depth + 1)
                )
                
    return connected_points

