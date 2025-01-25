def points_match(p1, p2, tolerance=0.01):
    """Helper function to check if two points match within tolerance"""
    return (abs(p1[0] - p2[0]) <= tolerance and 
            abs(p1[1] - p2[1]) <= tolerance)

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
