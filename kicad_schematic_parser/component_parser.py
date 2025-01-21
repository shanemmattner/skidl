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
    uuid: Optional[str] = None
    library: Optional[str] = None
    name: Optional[str] = None

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
            # Check indentation
            if not line.startswith("    "):
                result.add_error(line_num + i, line, "Property line must be indented with 4 spaces")
                continue

            # Split into key/value
            parts = line[4:].split(": ", 1)  # Skip indentation
            if len(parts) != 2:
                result.add_error(line_num + i, line, "Property line must be in format 'Key: Value'")
                continue

            key, value = parts[0].strip(), parts[1].strip()
            
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
            return result

        result.data = component
        return result
        
    except Exception as e:
        result.add_error(line_num, str(lines), f"Error parsing properties: {str(e)}")
        return result