"""Convert schematic sheet descriptions to SKiDL code.

Handles parsing of component, net, and label information from a text description
of a schematic sheet and generates equivalent SKiDL code.

Follows KISS and YAGNI principles - implements only what's needed with minimal complexity.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Component:
    """Simple data class for component information."""
    library: str
    part: str  
    reference: str
    value: str
    footprint: Optional[str] = None


@dataclass
class Net:
    """Simple data class for net information."""
    name: str
    pins: List[str]  # List of "component.pin" strings
    type: Optional[str] = None  # "power", "hierarchical", or None for local
    

def parse_netlist_section(text: str) -> Dict[str, Net]:
    """Parse netlist section to identify nets and their connections."""
    nets = {}
    current_net = None
    
    for line in text.split('\n'):
        line = line.strip()
        
        # Skip empty lines and section header
        if not line or line == "=== Netlist ===":
            continue
            
        # Start of new net
        if line.endswith(':'):
            current_net = line[:-1]  # Remove trailing colon
            nets[current_net] = Net(name=current_net, pins=[])
            continue
            
        # Look for pins or labels in current net
        if current_net and "Pin" in line and not line.startswith("Power") and not line.startswith("Hierarchical"):
            parts = line.split()
            component = parts[0]
            pin_num = parts[2]  # Format: "Component Pin X (~)"
            if not component.startswith('#PWR'):  # Skip power symbols
                nets[current_net].pins.append(f"{component}.{pin_num}")
                
        # Check for net type
        if current_net and "Power Labels:" in line:
            nets[current_net].type = "power"
        elif current_net and "Hierarchical Labels:" in line:
            nets[current_net].type = "hierarchical"
            
    return nets


def parse_component_section(text: str) -> List[Component]:
    """Parse components section to extract component information."""
    components = []
    current_component = None
    
    for line in text.split('\n'):
        line = line.strip()
        
        # Skip empty lines and section header
        if not line or line == "=== Components ===":
            continue
            
        # Start of new component
        if line.startswith("Component:"):
            if current_component:  # Store previous component if exists
                components.append(current_component)
            # Parse "Component: Library/Part"
            parts = line.split(': ')[1].split('/')
            current_component = Component(
                library=parts[0],
                part=parts[1],
                reference='',
                value=''
            )
            continue
            
        # Parse component properties
        if current_component and ':' in line:
            key, value = [x.strip() for x in line.split(':', 1)]
            if key == 'Reference':
                current_component.reference = value
            elif key == 'Value':
                current_component.value = value
            elif key == 'Footprint':
                current_component.footprint = value
                
    # Add final component
    if current_component:
        components.append(current_component)
        
    return components


def generate_skidl_code(name: str, components: List[Component], nets: Dict[str, Net]) -> str:
    """Generate SKiDL code from parsed components and nets."""
    # Determine circuit inputs/outputs from hierarchical nets
    inputs = []
    outputs = []
    for net in nets.values():
        if net.type == "hierarchical":
            if len(net.pins) == 1:  # Simple heuristic - single pin is input
                inputs.append(net.name.lower())
            else:
                outputs.append(net.name.lower())
    
    # Start with function definition
    params = ', '.join(inputs + outputs)
    code = [
        "@subcircuit",
        f"def {name}({params}):",
        "    # Create components"
    ]
    
    # Add component instantiations
    for comp in components:
        ref = comp.reference.lower()
        code.append(f"    {ref} = Part('{comp.library}', '{comp.part}', value='{comp.value}')")
    
    # Add connections
    code.append("\n    # Connect nets")
    for net_name, net in nets.items():
        if net.pins:  # Only generate connections for nets with pins
            pins = [p.lower() for p in net.pins]
            if net.type == "hierarchical":
                # Connect first pin to net and rest of pins
                code.append(f"    {pins[0]} += {net_name.lower()}" + 
                          (f", {', '.join(pins[1:])}" if len(pins) > 1 else ""))
            elif net.type == "power":
                code.append(f"    {pins[0]} += {net_name}" + 
                          (f", {', '.join(pins[1:])}" if len(pins) > 1 else ""))
            else:
                code.append(f"    {pins[0]} += {', '.join(pins[1:])}")
    
    return '\n'.join(code)


def sheet_to_skidl(sheet_name: str, text: str) -> str:
    """Convert a sheet description to SKiDL code.
    
    Args:
        sheet_name: Name to use for the generated SKiDL subcircuit
        text: Complete text description of the sheet
        
    Returns:
        Generated SKiDL code as a string
    """
    # Split into sections
    sections = {}
    current_section = None
    current_lines = []
    
    for line in text.split('\n'):
        if line.startswith('==='):
            if current_section:
                sections[current_section] = '\n'.join(current_lines)
            current_section = line.strip('= ')
            current_lines = []
        else:
            current_lines.append(line)
            
    if current_section:
        sections[current_section] = '\n'.join(current_lines)
        
    # Parse sections
    components = parse_component_section(sections.get('Components', ''))
    nets = parse_netlist_section(sections.get('Netlist', ''))
    
    # Generate code
    return generate_skidl_code(sheet_name, components, nets)