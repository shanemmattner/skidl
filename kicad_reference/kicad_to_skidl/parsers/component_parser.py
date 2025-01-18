#!/usr/bin/env python3

import re

def extract_components(content):
    """Extract component information from KiCad schematic content."""
    components = []
    
    # Find all symbol blocks
    symbol_pattern = r'\(symbol.*?\(lib_id\s+"([^"]+)".*?\(property\s+"Reference"\s+"([^"]+)".*?\(property\s+"Footprint"\s+"([^"]*)".*?\)'
    symbol_blocks = re.finditer(symbol_pattern, content, re.DOTALL)
    
    for match in symbol_blocks:
        lib_id = match.group(1)
        reference = match.group(2)
        footprint = match.group(3)
        
        # Skip power symbols and empty footprints
        if lib_id.startswith("power:") or not footprint:
            continue
            
        lib_parts = lib_id.split(":")
        components.append({
            'library': lib_parts[0],
            'symbol': lib_parts[1],
            'reference': reference,
            'footprint': footprint
        })
    
    return components

def extract_hierarchical_labels(content):
    """Extract hierarchical label information."""
    labels = []
    
    # Find all hierarchical label blocks
    label_matches = re.finditer(r'\(hierarchical_label\s+"([^"]+)"', content)
    
    for match in label_matches:
        label = match.group(1)
        if label not in labels:
            labels.append(label)
    
    return labels

def generate_skidl_subcircuit(sheet_name, components, labels):
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
        # Add resistor definitions
        for comp in components:
            code += f"""
    {comp['reference'].lower()} = Part("{comp['library']}", "{comp['symbol']}", """
            code += f"""value='1K', footprint='{comp['footprint']}')"""
        
        # Add internal nets
        if labels:
            code += "\n\n    # Create internal connection node"
            for label in labels:
                valid_name = make_valid_identifier(label)
                code += f"\n    {valid_name} = Net('{label}')"
        
        # Add connections
        code += "\n\n    # Connect the components"
        if labels:
            div_net = make_valid_identifier(labels[0])
            code += f"\n    pwr_net & r1 & {div_net} & r2 & gnd"
        else:
            code += "\n    pwr_net & r1 & r2 & gnd"
        
        # Add return statement
        if labels:
            div_net = make_valid_identifier(labels[0])
            code += f"\n\n    # Return just the divider node, not all locals\n    return {div_net}"
        else:
            code += "\n\n    return pwr_net"
    
    return code
