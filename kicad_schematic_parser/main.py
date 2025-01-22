from dataclasses import dataclass
from typing import List, Optional, Dict
import re

@dataclass
class Component:
    """Class to store component data"""
    reference: str
    value: str
    library: str
    name: str
    footprint: Optional[str] = None
    datasheet: Optional[str] = None
    description: Optional[str] = None
    position: Optional[tuple] = None
    angle: Optional[float] = None

def parse_kicad_analysis(content: str) -> List[Component]:
    """Parse a KiCad schematic analysis file and extract components.
    
    Args:
        content: String containing the full file content
        
    Returns:
        List of Component objects
    """
    components = []
    in_components_section = False
    current_component = None
    in_properties = False
    
    # Split content into lines and process
    lines = content.split('\n')
    for line in lines:
        stripped_line = line.strip()
        
        # Check for components section
        if stripped_line == "=== Components ===":
            in_components_section = True
            continue
            
        # Skip if not in components section
        if not in_components_section:
            continue
            
        # Check for end of components section
        if stripped_line.startswith("=== ") and stripped_line != "=== Components ===":
            in_components_section = False
            continue
            
        # Look for component definitions
        if stripped_line.startswith("Component: "):
            if current_component is not None and current_component['reference'] and current_component['value']:
                components.append(Component(**current_component))
            
            # Parse component library and name
            try:
                _, lib_name = stripped_line.split("Component: ")
                library, name = lib_name.split('/')
                current_component = {
                    'library': library,
                    'name': name,
                    'reference': '',
                    'value': '',
                    'footprint': None,
                    'datasheet': None,
                    'description': None,
                    'position': None,
                    'angle': None
                }
                in_properties = False
            except:
                current_component = None
                
        # Look for properties section
        elif stripped_line == "Properties:" and current_component:
            in_properties = True
            
        # Parse property lines
        elif in_properties and current_component and stripped_line:
            try:
                if line.startswith('\t\t'):  # Properties are indented with tabs
                    key, value = [x.strip() for x in stripped_line.split(':', 1)]
                    if key == 'Reference':
                        current_component['reference'] = value
                    elif key == 'Value':
                        current_component['value'] = value
                    elif key == 'Footprint':
                        current_component['footprint'] = value if value != "" else None
                    elif key == 'Datasheet':
                        current_component['datasheet'] = value if value != "~" else None
                    elif key == 'Description':
                        current_component['description'] = value
            except:
                pass
                
        # Look for position
        elif current_component and "Position: " in stripped_line:
            try:
                pos_str = stripped_line.split('Position: ')[1].split(',')
                x = float(pos_str[0].strip('( '))
                y = float(pos_str[1].strip(' )'))
                current_component['position'] = (x, y)
            except:
                pass
                
        # Look for angle
        elif current_component and "Angle: " in stripped_line:
            try:
                current_component['angle'] = float(stripped_line.split('Angle: ')[1])
            except:
                pass
    
    # Add the last component if there is one
    if current_component is not None and current_component['reference'] and current_component['value']:
        components.append(Component(**current_component))
    
    return components

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python kicad_parser.py <analysis_file>")
        sys.exit(1)
        
    try:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
            
        components = parse_kicad_analysis(content)
        
        # Print summary
        print(f"\nFound {len(components)} components:\n")
        
        # Group by library
        by_library = {}
        for comp in components:
            if comp.library not in by_library:
                by_library[comp.library] = []
            by_library[comp.library].append(comp)
            
        # First print BOM summary
        print("Bill of Materials Summary:")
        print("\nCount | Value | Footprint | Description")
        print("-" * 60)
        
        # Group by unique components (same value, footprint, and library)
        bom_groups = {}
        for comp in components:
            key = (comp.library, comp.value, comp.footprint or "No Footprint")
            if key not in bom_groups:
                bom_groups[key] = {
                    'count': 0,
                    'refs': [],
                    'description': comp.description
                }
            bom_groups[key]['count'] += 1
            bom_groups[key]['refs'].append(comp.reference)
        
        # Print BOM
        for key, group in sorted(bom_groups.items()):
            library, value, footprint = key
            print(f"{group['count']:5d} | {value:20s} | {footprint:30s} | {group['description'] or ''}")
            print(f"      References: {', '.join(sorted(group['refs']))}")
        
        print("\nDetailed Component Listing:")
        # Print organized detailed summary
        for library in sorted(by_library.keys()):
            print(f"\nLibrary: {library}")
            for comp in sorted(by_library[library], key=lambda x: x.reference):
                print(f"  {comp.reference}: {comp.value} ({comp.name})")
                if comp.footprint:
                    print(f"    Footprint: {comp.footprint}")
                if comp.description:
                    print(f"    Description: {comp.description}")
                if comp.position:
                    print(f"    Position: ({comp.position[0]}, {comp.position[1]})")
                    if comp.angle is not None:
                        print(f"    Angle: {comp.angle}°")
                        
    except FileNotFoundError:
        print(f"Error: Could not find file '{sys.argv[1]}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()