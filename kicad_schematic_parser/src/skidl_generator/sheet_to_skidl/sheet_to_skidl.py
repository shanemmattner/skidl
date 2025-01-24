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
    in_properties = False
    
    for line in text.split('\n'):
        line_stripped = line.strip()
        
        if not line_stripped:
            continue
            
        if line_stripped == "=== Components ===":
            in_component_section = True
            continue
            
        if not in_component_section:
            continue
            
        if line_stripped.startswith("=== ") and line_stripped != "=== Components ===":
            break
            
        if line_stripped.startswith("Component:"):
            if current_component:
                components.append(current_component)
            lib_part = line_stripped.split(': ')[1]
            if '/' in lib_part:
                lib, part = lib_part.split('/')
                current_component = Component(
                    library=lib.strip(),
                    part=part.strip(),
                    reference='',
                    value='',
                    footprint=None
                )
        elif current_component and line_stripped == "Properties:":
            in_properties = True
        elif current_component and in_properties and line.startswith('\t\t'):  # Check for double tab
            key, value = [x.strip() for x in line_stripped.split(':', 1)]
            if key == 'Reference':
                current_component.reference = value
            elif key == 'Value':
                current_component.value = value
            elif key == 'Footprint':
                current_component.footprint = value if value else None
        elif not line.startswith('\t'):  # Reset properties flag when indentation ends
            in_properties = False
                
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
    params = ', '.join(sorted(inputs + outputs))
    
    lines = [
        "@subcircuit",
        f"def {name}({params}):",
        "    # Create components"
    ]
    
    # Sort components by reference for consistent output
    for comp in sorted(components, key=lambda x: x.reference.lower()):
        ref = comp.reference.lower()
        lines.append(f"    {ref} = Part('{comp.library}', '{comp.part}', value='{comp.value}')")
    
    lines.append("\n    # Connect nets")
    
    # Process local nets first, then power nets, then hierarchical nets
    def format_pin(pin: str) -> str:
        comp, pin_num = pin.split('.')
        return f"{comp.lower()}[{pin_num}]"
    
    # Handle hierarchical pins (VIN, VOUT)
    for net_name, net in sorted(nets.items(), key=lambda x: x[0].lower()):
        if net.type == "hierarchical":
            formatted_pins = [format_pin(pin) for pin in sorted(net.pins)]
            if len(formatted_pins) == 1:  # Input net
                lines.append(f"    {formatted_pins[0]} += {net_name.lower()}")
            
    # Handle internal connections and power nets
    for net_name, net in sorted(nets.items(), key=lambda x: x[0].lower()):
        if net.type == "hierarchical" and len(net.pins) == 1:
            continue  # Skip input nets already handled
            
        formatted_pins = [format_pin(pin) for pin in sorted(net.pins)]
        if not formatted_pins:
            continue
            
        first_pin, *rest_pins = formatted_pins
        if net_name == "GND":
            suffix = f", GND"
        elif net.type == "hierarchical":
            suffix = f", {net_name.lower()}"
        else:
            suffix = ""
            
        line = f"    {first_pin} +="
        if rest_pins:
            line += " " + ", ".join(rest_pins)
        if suffix:
            line += suffix
            
        lines.append(line)
    
    return '\n'.join(lines)


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