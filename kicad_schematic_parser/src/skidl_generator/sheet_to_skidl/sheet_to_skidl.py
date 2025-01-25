"""Convert schematic sheet descriptions to SKiDL code.

Handles parsing of component, net, and label information from a text description
of a schematic sheet and generates equivalent SKiDL code.

Follows KISS and YAGNI principles - implements only what's needed with minimal complexity.
"""

import re

from dataclasses import dataclass
from typing import Dict, List, Optional


from abc import ABC, abstractmethod

class ParserStrategy(ABC):
    """Abstract base class for component parsing strategies."""
    @abstractmethod
    def parse(self, line: str, component: "Component") -> None:
        pass

class BasicComponentParser(ParserStrategy):
    """Default strategy for parsing standard components"""
    def parse(self, line: str, component: "Component") -> None:
        key, value = [x.strip() for x in line.split(':', 1)]
        if key == 'Reference':
            component.reference = value
        elif key == 'Value':
            component.value = value
        elif key == 'Footprint':
            component.footprint = value if value else None

class BaseComponent(ABC):
    """Abstract base class for component representations."""
    @property
    @abstractmethod
    def skidl_part_expression(self) -> str:
        pass

@dataclass
class Component(BaseComponent):
    """Concrete component implementation for KiCad schematic data."""
    library: str
    part: str  
    reference: str
    value: str
    footprint: Optional[str] = None
    _parser_strategy: ParserStrategy = BasicComponentParser()

    @classmethod
    def set_parser_strategy(cls, strategy: ParserStrategy):
        cls._parser_strategy = strategy

    @property
    def skidl_part_expression(self) -> str:
        return self._parser_strategy.parse_expression(self)

    def parse_property(self, line: str):
        self._parser_strategy.parse(line, self)


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
        line_stripped = line.strip()
        if not line_stripped or line_stripped == "=== Netlist ===":
            continue

        if line.endswith(':'):
            # Handle section headers and net names
            if line_stripped == "Hierarchical Labels:":
                if current_net:
                    nets[current_net].type = "hierarchical"
                current_net = None
            else:
                # New net definition (line ends with ':')
                current_net = line_stripped[:-1].strip()  # Remove colon and whitespace
                nets[current_net] = Net(name=current_net, pins=[])
        elif current_net and line.startswith('\t'):
            # Process pin lines (indented with tab)
            pin_line = line_stripped
            if "Pin" in pin_line:
                try:
                    # Split on colon to separate pin info from position
                    pin_info = pin_line.split(':', 1)[0].strip()
                    parts = pin_info.split()
                    if len(parts) >= 3 and parts[1] == 'Pin':
                        component = parts[0]
                        pin_num = parts[2].strip('()~:')
                        if not component.startswith('#PWR'):
                            nets[current_net].pins.append(f"{component}.{pin_num}")
                except (IndexError, ValueError) as e:
                    print(f"Warning: Skipping malformed pin line: {pin_line}")
                    continue

    # Detect power nets using expanded regex pattern
    POWER_NET_PATTERN = re.compile(
        r'^(\+?\d+\.?\d*[vV](?:olt)?s?|GND|gnd|ground)$',  # Matches +5V, 3.3V, +3.3Volts, GND, etc.
        flags=re.IGNORECASE
    )
    
    for net in nets.values():
        if POWER_NET_PATTERN.match(net.name):
            net.type = "power"

    return nets

class ComponentValidator:
    """Validation layer for component data integrity"""
    @classmethod
    def validate(cls, component: Component) -> bool:
        """Check required fields and basic formatting"""
        if not all([component.library, component.part, component.reference]):
            print(f"Invalid component missing required fields: {component}")
            return False
        return True

def parse_component_section(text: str, validator: ComponentValidator = ComponentValidator()) -> List[Component]:
    """Parse components section with validation and error handling"""
    components = []
    current_component = None
    in_component_section = False
    in_properties = False
    error_count = 0
    
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
            current_component.parse_property(line_stripped)
        elif not line.startswith('\t'):  # Reset properties flag when indentation ends
            in_properties = False
                
    # Validate and add component
    if current_component:
        if validator.validate(current_component):
            components.append(current_component)
        else:
            error_count += 1
            print(f"Skipping invalid component: {current_component.reference}")
        
    return components

def generate_skidl_code(name: str, components: List[Component], nets: Dict[str, Net]) -> str:
    """Generate SKiDL code from component and net information.
    
    Args:
        name: Name of the subcircuit to generate
        components: List of Component objects defining the circuit elements
        nets: Dictionary of Net objects defining connections
        
    Returns:
        String containing complete SKiDL subcircuit code
    """
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
    
    # Start building code sections
    lines = [
        "@subcircuit",
        f"def {name}({params}):",
        "    # Create components"
    ]
    
    # Add component definitions - ensuring they exist before net references
    for comp in sorted(components, key=lambda x: x.reference.lower()):
        ref = comp.reference.lower()
        lines.append(f"    {ref} = Part('{comp.library}', '{comp.part}', value='{comp.value}')")
    
    # Add empty line between sections for readability
    lines.append("")
    
    # Add net section header
    lines.append("    # Connect nets")

    def format_pin(pin: str) -> str:
        """Helper function to format pin references consistently."""
        comp, pin_num = pin.split('.')
        return f"{comp.lower()}[{pin_num}]"

    # Process nets in a deterministic order
    processed_nets = {}
    
    # First process hierarchical inputs
    for net_name, net in sorted(nets.items()):
        if net.type == "hierarchical" and len(net.pins) == 1:
            pin = format_pin(net.pins[0])
            processed_nets[net_name] = f"    {pin} += {net_name.lower()}"

    # Then process hierarchical outputs and local nets
    for net_name, net in sorted(nets.items()):
        if net_name in processed_nets or not net.pins:
            continue
            
        if net.type != "power":
            pins = [format_pin(pin) for pin in sorted(net.pins)]
            first_pin = pins[0]
            other_parts = pins[1:]
            
            if net.type == "hierarchical":
                other_parts.append(net_name.lower())
                
            if other_parts:  # Only create connection if there are pins to connect
                processed_nets[net_name] = f"    {first_pin} += {', '.join(other_parts)}"

    # Finally process power nets (like GND)
    for net_name, net in sorted(nets.items()):
        if net_name in processed_nets or not net.pins:
            continue
            
        if net.type == "power":
            pins = [format_pin(pin) for pin in sorted(net.pins)]
            first_pin = pins[0]
            other_parts = pins[1:]
            
            # Add power net connection
            other_parts.append(net.name)
                
            if other_parts:  # Only create connection if there are pins to connect
                processed_nets[net_name] = f"    {first_pin} += {', '.join(other_parts)}"

    # Add nets in sorted order for consistent output
    for name in sorted(processed_nets):
        lines.append(processed_nets[name])

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
            current_section = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
            
    if current_section:
        sections[current_section] = '\n'.join(current_lines)
        
    # Parse sections - pass the complete section text including header
    components = parse_component_section(text)  # Pass full text to let parser handle section detection
    nets = parse_netlist_section(text)  # Pass full text to let parser handle section detection
    
    # Generate code
    return generate_skidl_code(sheet_name, components, nets)
