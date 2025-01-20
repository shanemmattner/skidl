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

def get_connected_points(start_pos, wire_list, visited=None, tolerance=0.01):
    """
    Find all points connected to start_pos through wires, recursively
    
    Args:
        start_pos: Starting point (x,y) tuple
        wire_list: List of wire connections
        visited: Set of already visited wire segments
        tolerance: Distance tolerance for point matching
        
    Returns:
        set: Set of all connected points including points along wire segments
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
        
        # Check if this wire connects to our point at endpoints or along segment
        if (points_match(start_pos, wire_start, tolerance) or 
            points_match(start_pos, wire_end, tolerance) or 
            point_on_wire_segment(start_pos, wire_start, wire_end, tolerance)):
            
            # Add both endpoints since the point connects to this wire
            connected_points.add(wire_start)
            connected_points.add(wire_end)
            
            # Recursively find other connected points from both endpoints
            connected_points.update(
                get_connected_points(wire_start, wire_list, visited, tolerance)
            )
            connected_points.update(
                get_connected_points(wire_end, wire_list, visited, tolerance)
            )
                
    return connected_points
