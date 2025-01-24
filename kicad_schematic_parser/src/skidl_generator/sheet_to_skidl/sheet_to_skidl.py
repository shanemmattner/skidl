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
    nets = {}
    current_net = None
    in_power_section = False
    
    for line in text.split('\n'):
        line = line.strip()
        if not line or line == "=== Netlist ===":
            continue
            
        if line.endswith(':'):
            if line == "Power Labels:":
                if current_net:
                    nets[current_net].type = "power"
            elif line == "Hierarchical Labels:":
                if current_net:
                    nets[current_net].type = "hierarchical"
            elif not line.startswith('\t'):  # New net
                current_net = line[:-1]
                nets[current_net] = Net(name=current_net, pins=[])
        elif current_net and "Pin" in line and not line.startswith('\t'):
            component = line.split()[0]
            pin_num = line.split()[2]
            if not component.startswith('#PWR'):
                nets[current_net].pins.append(f"{component}.{pin_num}")

    # Set GND as power net if it exists
    if "GND" in nets:
        nets["GND"].type = "power"

    return nets


def parse_component_section(text: str) -> List[Component]:
    components = []
    current_component = None
    in_component_section = False
    
    for line in text.split('\n'):
        line = line.strip()
        
        if line == "=== Components ===":
            in_component_section = True
            continue
            
        if not in_component_section or not line:
            continue
            
        if line.startswith("==="):  # End of section
            break
            
        if line.startswith("Component:"):
            if current_component:
                components.append(current_component)
            lib_part = line.split(': ')[1]
            if '/' in lib_part:
                lib, part = lib_part.split('/')
                current_component = Component(
                    library=lib.strip(),
                    part=part.strip(),
                    reference='',
                    value='',
                    footprint=None
                )
        elif current_component and line.startswith('Properties:'):
            continue
        elif current_component and '\t' in line and ':' in line:
            key, value = [x.strip() for x in line.split(':', 1)]
            if key == 'Reference':
                current_component.reference = value
            elif key == 'Value':
                current_component.value = value
            elif key == 'Footprint':
                current_component.footprint = value if value else None
                
    if current_component:
        components.append(current_component)
        
    return components

def generate_skidl_code(name: str, components: List[Component], nets: Dict[str, Net]) -> str:
    # Find hierarchical nets (inputs/outputs)
    inputs = []
    outputs = []
    for net in nets.values():
        if net.type == "hierarchical":
            net_name = net.name.lower()
            if len(net.pins) == 1:
                inputs.append(net_name)
            else:
                outputs.append(net_name)

    # Sort params for consistent output
    params = ', '.join(sorted(inputs) + sorted(outputs))
    
    code = [
        "@subcircuit",
        f"def {name}({params}):",
        "    # Create components"
    ]
    
    # Sort components by reference for consistent output
    for comp in sorted(components, key=lambda x: x.reference.lower()):
        ref = comp.reference.lower()
        code.append(f"    {ref} = Part('{comp.library}', '{comp.part}', value='{comp.value}')")
    
    code.append("\n    # Connect nets")
    
    # Sort nets for consistent output
    for net_name, net in sorted(nets.items(), key=lambda x: x[0]):
        if not net.pins:
            continue
            
        # Convert pin format from comp.pin to comp[pin]
        formatted_pins = []
        for pin in net.pins:
            comp, pin_num = pin.split('.')
            formatted_pins.append(f"{comp.lower()}[{pin_num}]")
            
        if net_name == "GND":
            pin_str = ', '.join(sorted(formatted_pins))
            if pin_str:
                first_pin, *rest_pins = pin_str.split(', ')
                code.append(f"    {first_pin} += GND" + (f", {', '.join(rest_pins)}" if rest_pins else ""))
        elif net.type == "hierarchical":
            pin_str = ', '.join(sorted(formatted_pins))
            if pin_str:
                first_pin, *rest_pins = pin_str.split(', ')
                code.append(f"    {first_pin} += {net_name.lower()}" + 
                          (f", {', '.join(rest_pins)}" if rest_pins else ""))
            
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