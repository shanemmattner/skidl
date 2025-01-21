from component_parser import parse_component_name, parse_component_properties

def read_sections(filename):
    """Read and parse Component sections from hierarchy.txt
    
    Returns:
        List of tuples (component_line, property_lines)
    """
    sections = []
    current_section = None
    property_lines = []
    in_properties = False
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.rstrip()  # Remove trailing whitespace
            
            # Skip empty lines and section dividers
            if not line or line.startswith('--') or line.startswith('***'):
                if current_section:  # End current section if any
                    if property_lines:
                        sections.append((current_section, property_lines))
                    current_section = None
                    property_lines = []
                    in_properties = False
                continue
                
            # Start of new component section
            if line.startswith('Component:'):
                if current_section:  # Save previous section if any
                    if property_lines:
                        sections.append((current_section, property_lines))
                current_section = line
                property_lines = []
                in_properties = False
                continue
                
            # Inside Properties section
            if line.strip() == 'Properties:':
                in_properties = True
                property_lines = [line]
                continue
                
            if in_properties and line:
                property_lines.append(line)
                
    # Don't forget last section
    if current_section and property_lines:
        sections.append((current_section, property_lines))
        
    return sections

def main():
    # Read all sections
    sections = read_sections('hierachy.txt')
    
    print(f"Found {len(sections)} component sections")
    print("\nTesting component name parsing:")
    print("-" * 50)
    
    name_success = 0
    for i, (comp_line, _) in enumerate(sections, 1):
        result = parse_component_name(comp_line)
        if result.success:
            name_success += 1
            print(f"✓ {i}. Successfully parsed: {result.data}")
        else:
            print(f"✗ {i}. Failed to parse: {comp_line}")
            for error in result.errors:
                print(f"   Error: {error.message}")
    
    print(f"\nComponent name parsing success rate: {name_success}/{len(sections)}")
    
    print("\nTesting properties parsing:")
    print("-" * 50)
    
    prop_success = 0
    for i, (_, prop_lines) in enumerate(sections, 1):
        result = parse_component_properties(prop_lines)
        if result.success:
            prop_success += 1
            print(f"✓ {i}. Successfully parsed: {result.data.reference} ({result.data.value})")
        else:
            print(f"✗ {i}. Failed to parse properties:")
            for error in result.errors:
                print(f"   Error: {error.message}")
            print("   Lines:")
            for line in prop_lines:
                print(f"   {line}")
    
    print(f"\nProperties parsing success rate: {prop_success}/{len(sections)}")

if __name__ == '__main__':
    main()