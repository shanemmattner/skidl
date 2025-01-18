from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from dataclasses import dataclass
from ..parsers.base_parser import Component, Sheet

@dataclass
class CircuitConfig:
    """Configuration for circuit generation."""
    power_nets: List[str]
    default_values: Dict[str, Dict[str, str]]  # Component type -> default values mapping

class SubcircuitGenerator(ABC):
    """Abstract base class for subcircuit generators."""
    
    def __init__(self, config: CircuitConfig):
        self.config = config

    @abstractmethod
    def generate_subcircuit(self, sheet: Sheet) -> str:
        """Generate subcircuit code for a sheet."""
        pass

    def _make_valid_identifier(self, name: str) -> str:
        """Convert string to valid Python identifier."""
        return name.replace("-", "_").lower()

class SKiDLGenerator(SubcircuitGenerator):
    """SKiDL specific subcircuit generator."""
    
    def generate_subcircuit(self, sheet: Sheet) -> str:
        """Generate SKiDL subcircuit code."""
        code = [
            "from skidl import *",
            "",
            "# Define ground net",
            "gnd = Net('GND')",
            "gnd.drive = POWER",
            "gnd.do_erc = False",
            "",
            f"@subcircuit",
            f"def {sheet.name}(pwr_net):",
            f'    """Create a {sheet.name} subcircuit"""',
            "",
            "    # Create components"
        ]

        # Add component definitions
        for comp in sheet.components:
            ref = comp.reference.lower()
            default_values = self.config.default_values.get(comp.symbol, {})
            value = default_values.get('value', '')
            
            comp_def = [
                f"    {ref} = Part(",
                f'        "{comp.library}",',
                f'        "{comp.symbol}",',
            ]
            
            if value:
                comp_def.append(f"        value='{value}',")
            
            comp_def.append(f"        footprint='{comp.footprint}'")
            comp_def.append("    )")
            
            code.extend(comp_def)
            code.append("")

        # Add internal nets for hierarchical labels
        if sheet.labels:
            code.extend([
                "    # Create internal connection nodes",
                *[f"    {self._make_valid_identifier(label)} = Net('{label}')"
                  for label in sheet.labels],
                ""
            ])

        # Add connections based on sheet type
        code.append("    # Connect components")
        if sheet.name == "power2":
            code.extend(self._generate_power2_connections())
        else:  # Default to voltage divider type connections
            code.extend(self._generate_divider_connections(sheet))

        # Add return statement
        if sheet.labels:
            div_net = self._make_valid_identifier(sheet.labels[0])
            code.extend([
                "",
                f"    return {div_net}"
            ])
        else:
            code.extend([
                "",
                "    return pwr_net"
            ])

        return "\n".join(code)

    def _generate_power2_connections(self) -> List[str]:
        """Generate connections for power2 subcircuit."""
        return [
            "    # Create power nets",
            "    vcc_3v3 = Net('+3V3')",
            "    vcc_3v3.drive = POWER",
            "",
            "    # Connect power input side",
            "    pwr_net & c1 & gnd",
            "    pwr_net += u1['VI']",
            "",
            "    # Connect power output side",
            "    u1['VO'] += vcc_3v3",
            "    vcc_3v3 & c2 & gnd",
            "",
            "    # Connect ground",
            "    u1['GND'] += gnd"
        ]

    def _generate_divider_connections(self, sheet: Sheet) -> List[str]:
        """Generate connections for voltage divider subcircuit."""
        connections = []
        if sheet.labels:
            div_net = self._make_valid_identifier(sheet.labels[0])
            connections.append(f"    pwr_net & r1 & {div_net} & r2 & gnd")
        else:
            connections.append("    pwr_net & r1 & r2 & gnd")
        return connections
