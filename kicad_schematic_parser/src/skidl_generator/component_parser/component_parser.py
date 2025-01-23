from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ParseError:
    """Class to store parsing error details"""
    line_num: int
    line: str
    message: str

class ParseResult:
    """Class to store parsing results and any errors"""
    def __init__(self):
        self.success = True
        self.errors = []
        self.data = None
    
    def add_error(self, line_num: int, line: str, message: str):
        self.errors.append(ParseError(line_num, line, message))
        self.success = False

@dataclass
class Component:
    """Class to store component data"""
    reference: str
    value: str
    footprint: Optional[str] = None
    datasheet: Optional[str] = None
    description: Optional[str] = None
    library: Optional[str] = None  # e.g. "Device"
    name: Optional[str] = None     # e.g. "R"
    position: Optional[tuple] = None
    angle: Optional[float] = None
    uuid: Optional[str] = None

def parse_component_block(lines: List[str]) -> ParseResult:
    """Parse a complete component block including header, properties, and position."""
    result = ParseResult()
    component = Component(reference="", value="")
    
    try:
        if not lines:
            result.add_error(0, "", "Empty component block")
            return result
            
        # Parse component header (library/name)
        header = lines[0].strip()
        name_result = parse_component_name(header)
        if not name_result.success:
            result.errors.extend(name_result.errors)
            return result
            
        library, name = name_result.data
        component.library = library
        component.name = name
        
        # Find property section
        prop_start = None
        for i, line in enumerate(lines):
            if line.strip() == "Properties:":
                prop_start = i
                break
                
        if prop_start is None:
            result.add_error(0, str(lines), "No Properties section found")
            return result
            
        # Parse properties
        prop_lines = []
        i = prop_start + 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("Position:"):
            line = lines[i].strip()
            if line:  # Skip empty lines
                prop_lines.append(line)
            i += 1
            
        # Parse position if present
        for line in lines:
            line = line.strip()
            if line.startswith("Position:"):
                try:
                    # Extract position and angle from format: Position: (x, y), Angle: z
                    pos_str = line[line.find("(")+1:line.find(")")]
                    pos_angle = [float(x.strip()) for x in pos_str.split(",")]
                    component.position = (pos_angle[0], pos_angle[1])
                    if "Angle:" in line:
                        component.angle = float(line.split("Angle:")[-1].strip())
                except Exception as e:
                    result.add_error(0, line, f"Error parsing position: {str(e)}")
                    
        # Process properties
        for line in prop_lines:
            if ":" not in line:
                continue
            key, value = [x.strip() for x in line.split(":", 1)]
            
            if key == "Reference":
                component.reference = value
            elif key == "Value":
                component.value = value
            elif key == "Footprint":
                component.footprint = value
            elif key == "Datasheet":
                component.datasheet = value
            elif key == "Description":
                component.description = value
                
        # Validate required fields
        if not component.reference or not component.value:
            result.add_error(0, str(lines), "Component must have Reference and Value")
            return result
            
        result.data = component
        return result
        
    except Exception as e:
        result.add_error(0, str(lines), f"Error parsing component block: {str(e)}")
        return result

def parse_component_name(line: str, line_num: int = 1) -> ParseResult:
    """Parse a component line to extract library and part name.
    
    Args:
        line: String containing component line from hierarchy.txt
        line_num: Line number in source file (for error reporting)
        
    Returns:
        ParseResult containing:
            - On success: data tuple of (library_name, component_name)
            - On error: error details
    """
    result = ParseResult()
    
    # Basic format validation
    if not line.startswith("Component:"):
        result.add_error(line_num, line, "Line must start with 'Component:'")
        return result
        
    # Extract the library/component part after "Component:"
    try:
        lib_comp = line.split(": ")[1].strip()
        
        # Must contain exactly one forward slash
        if lib_comp.count("/") != 1:
            result.add_error(line_num, line, 
                "Component must be in format 'library_name/component_name'")
            return result
            
        # Split into library and component names
        library, component = lib_comp.split("/")
        
        # Basic validation of library and component names
        if not library or not component:
            result.add_error(line_num, line,
                "Both library and component names must not be empty")
            return result
            
        result.data = (library, component)
        return result
        
    except IndexError:
        result.add_error(line_num, line, 
            "Invalid component line format")
        return result

def parse_component_properties(lines: List[str], line_num: int = 1) -> ParseResult:
    """Parse component properties section.
    
    Args:
        lines: List of strings containing properties section
        line_num: Starting line number for error reporting
        
    Returns:
        ParseResult containing:
            - On success: Component object with parsed properties
            - On error: error details
    """
    result = ParseResult()
    
    # Basic format validation
    if not lines or lines[0].strip() != "Properties:":
        result.add_error(line_num, str(lines), "Section must start with 'Properties:'")
        return result

    # Initialize component with required fields
    component = Component(reference="", value="")
    
    try:
        for i, line in enumerate(lines[1:], start=1):
            # Check for proper indentation
            if not line.startswith('    ') and not line.startswith('\t'):
                result.add_error(line_num + i, line, f"Property line must be indented: {line}")
            
            line = line.rstrip()  # Remove trailing whitespace
            if not line:  # Skip empty lines
                continue

            # Get the indented content, handling both tabs and spaces
            stripped_line = line.lstrip('\t ')
            
            # Validate property line format
            if ':' not in stripped_line:
                result.add_error(line_num + i, line, f"Property line must be in format 'Key: Value': {line}")
                continue

            # Split into key/value
            parts = stripped_line.split(':', 1)  # Split on first colon

            # Validate key and value
            if len(parts) != 2:
                result.add_error(line_num + i, line, f"Property line must be in format 'Key: Value': {line}")
                continue

            key, value = parts[0].strip(), parts[1].strip()
            
            # Validate key and value are not empty
            if not key:
                result.add_error(line_num + i, line, f"Property key cannot be empty: {line}")
            
            if not value:
                result.add_error(line_num + i, line, f"Property value cannot be empty: {line}")
            
            # Set component attribute based on property key
            if key == "Reference":
                component.reference = value
            elif key == "Value":
                component.value = value
            elif key == "Footprint":
                component.footprint = value
            elif key == "Datasheet":
                component.datasheet = value
            elif key == "Description":
                component.description = value
            elif key == "UUID":
                component.uuid = value

        # Validate required fields
        if not component.reference or not component.value:
            result.add_error(line_num, str(lines), "Component must have Reference and Value")

        # If any errors occurred, return without setting data
        if result.errors:
            return result

        result.data = component
        return result
        
    except Exception as e:
        result.add_error(line_num, str(lines), f"Error parsing properties: {str(e)}")
        return result
