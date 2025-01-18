#!/usr/bin/env python3

import re
from typing import List
from .base_parser import Label, KiCadSchematicParser

def extract_components(content):
    """Extract component information from KiCad schematic content."""
    components = []
    
    # Find all symbol blocks with position
    symbol_pattern = r'\(symbol\s+\(lib_id\s+"([^"]+)"\).*?\(at\s+(\d+\.?\d*)\s+(\d+\.?\d*)[^)]*\).*?\(property\s+"Reference"\s+"([^"]+)".*?\(property\s+"Footprint"\s+"([^"]*)"'
    symbol_blocks = re.finditer(symbol_pattern, content, re.DOTALL)
    
    for match in symbol_blocks:
        lib_id = match.group(1)
        x = float(match.group(2))
        y = float(match.group(3))
        reference = match.group(4)
        footprint = match.group(5)
        
        # Skip power symbols and empty footprints
        if lib_id.startswith("power:") or not footprint:
            continue
            
        lib_parts = lib_id.split(":")
        components.append({
            'library': lib_parts[0],
            'symbol': lib_parts[1],
            'reference': reference,
            'footprint': footprint,
            'x': x,
            'y': y,
            'pin1_y': y + 3.81,  # Pin 1 is 3.81 units above center
            'pin2_y': y - 3.81   # Pin 2 is 3.81 units below center
        })
    
    return components

def extract_hierarchical_labels(content):
    """Extract hierarchical label information with positions."""
    from .base_parser import Label
    
    parser = KiCadSchematicParser()
    labels = parser.parse_labels(content)
    
    # Deduplicate labels by name, keeping the first occurrence
    seen_names = set()
    unique_labels = []
    for label in labels:
        if label.name not in seen_names:
            seen_names.add(label.name)
            unique_labels.append(label)
    
    return unique_labels

def generate_skidl_subcircuit(sheet_name, components, labels: List[Label]):
    """Generate SKiDL subcircuit code."""
    # Convert label to valid Python identifier
    def make_valid_identifier(name):
        return name.replace("-", "_").lower()
    
    code = f"""from skidl import *

# Define ground net
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

@subcircuit
def {sheet_name}(pwr_net):
    \"\"\"Create a {sheet_name} subcircuit\"\"\"
"""
    
    # Handle power2 subcircuit specially
    if sheet_name == "power2":
        code += """    # Create power nets
    vcc_3v3 = Net('+3V3')
    vcc_3v3.drive = POWER
    
    # Create components"""
        
        # Add component definitions with proper values
        for comp in components:
            ref = comp['reference'].lower()
            if comp['symbol'] == 'C':
                code += f"""
    {ref} = Part("{comp['library']}", "{comp['symbol']}", """
                code += f"""value='10uF', footprint='{comp['footprint']}')"""
            else:  # Regulator
                code += f"""
    {ref} = Part("{comp['library']}", "{comp['symbol']}", """
                code += f"""footprint='{comp['footprint']}')"""
        
        # Add power2 specific connections
        code += """

    # Connect power input side
    pwr_net & c1 & gnd
    pwr_net += u1['VI']
    
    # Connect power output side
    u1['VO'] += vcc_3v3
    vcc_3v3 & c2 & gnd
    
    # Connect ground
    u1['GND'] += gnd
    
    return vcc_3v3"""
        
    else:  # resistor_divider subcircuit
        code += "    # Create components"
        # Sort components by y position
        components.sort(key=lambda x: x['y'])
        
        # Add resistor definitions
        for comp in components:
            code += f"""
    {comp['reference'].lower()} = Part("{comp['library']}", "{comp['symbol']}", """
            code += f"""value='1K', footprint='{comp['footprint']}')"""
        
        # Add internal nets for labels
        if labels:
            code += "\n\n    # Create internal connection nodes"
            for label in labels:
                valid_name = make_valid_identifier(label.name)
                code += f"\n    {valid_name} = Net('{label.name}')"
        
        # Match labels to pins and create connections
        code += "\n\n    # Connect the components"
        
        # Create connections based on y-coordinates
        code += "\n    # Connect power to first resistor"
        code += f"\n    pwr_net & {components[0]['reference'].lower()}"
        
        # Connect middle point between resistors using label
        if labels:
            div_net = make_valid_identifier(labels[0].name)
            code += f"\n\n    # Connect divider node"
            code += f"\n    {components[0]['reference'].lower()} & {div_net}"
            code += f"\n    {div_net} & {components[1]['reference'].lower()}"
        else:
            # Direct connection if no label
            code += f" & {components[1]['reference'].lower()}"
        
        # Connect to ground
        code += "\n\n    # Connect to ground"
        code += f"\n    {components[1]['reference'].lower()} & gnd"
        
        # Add return statement
        if labels:
            div_net = make_valid_identifier(labels[0].name)
            code += f"\n\n    # Return just the divider node, not all locals\n    return {div_net}"
        else:
            code += "\n\n    return pwr_net"
    
    return code
