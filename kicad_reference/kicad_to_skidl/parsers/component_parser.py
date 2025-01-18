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
    
    # Create power nets if this is a power subcircuit
    if sheet_name.startswith("power"):
        code += """    # Create power nets
    vcc_3v3 = Net('+3V3')
    vcc_3v3.drive = POWER
    """
    
    code += "    # Create components"
    # Sort components by y position
    components.sort(key=lambda x: x['y'])
    
    # Add component definitions
    for comp in components:
        ref = comp['reference'].lower()
        if comp['symbol'] == 'C':
            code += f"""
    {ref} = Part("{comp['library']}", "{comp['symbol']}", """
            code += f"""value='10uF', footprint='{comp['footprint']}')"""
        elif comp['symbol'] == 'R':
            code += f"""
    {ref} = Part("{comp['library']}", "{comp['symbol']}", """
            code += f"""value='1K', footprint='{comp['footprint']}')"""
        else:
            code += f"""
    {ref} = Part("{comp['library']}", "{comp['symbol']}", """
            code += f"""footprint='{comp['footprint']}')"""
    
    # Add internal nets for labels if we have multiple components
    if len(components) > 1 and labels:
        code += "\n\n    # Create internal connection nodes"
        for label in labels:
            valid_name = make_valid_identifier(label.name)
            code += f"\n    {valid_name} = Net('{label.name}')"
    
    # Create component connections based on sheet type
    code += "\n\n    # Connect the components"
    
    # Handle different types of components and their connections
    if len(components) > 0:
        # Check for special components
        regulator = next((c for c in components if c['symbol'].startswith('NCP1117')), None)
        mcu = next((c for c in components if c['symbol'].startswith('STM32')), None)
        caps = [c for c in components if c['symbol'] == 'C']
        resistors = [c for c in components if c['symbol'] == 'R']
        
        if sheet_name.startswith("power") and regulator:
            # Handle power regulator subcircuit
            reg_ref = regulator['reference'].lower()
            code += f"\n    # Connect regulator input"
            code += f"\n    pwr_net += {reg_ref}['VI']"
            code += f"\n    {reg_ref}['GND'] += gnd"
            code += f"\n    {reg_ref}['VO'] += vcc_3v3"
            
            # Connect capacitors if present
            for cap in caps:
                cap_ref = cap['reference'].lower()
                if caps.index(cap) == 0:  # Input capacitor
                    code += f"\n\n    # Connect input capacitor"
                    code += f"\n    pwr_net & {cap_ref} & gnd"
                else:  # Output capacitor
                    code += f"\n\n    # Connect output capacitor"
                    code += f"\n    vcc_3v3 & {cap_ref} & gnd"
            
            code += "\n\n    return vcc_3v3"
            
        elif mcu:
            # Handle microcontroller connections
            mcu_ref = mcu['reference'].lower()
            code += f"\n    # Connect MCU power pins"
            code += f"\n    pwr_net += {mcu_ref}['VDD']"
            code += f"\n    {mcu_ref}['VSS'] += gnd"
            code += f"\n    {mcu_ref}['VSSA'] += gnd"
            code += f"\n    {mcu_ref}['VDDA'] += pwr_net"
            
            code += "\n\n    return pwr_net"
            
        elif resistors:
            # Handle resistor networks (like voltage dividers)
            if len(resistors) == 1:
                # Single resistor
                code += "\n    # Connect single resistor"
                code += f"\n    pwr_net & {resistors[0]['reference'].lower()} & gnd"
            else:
                # Multiple resistors in series
                code += "\n    # Connect resistors in series"
                for i, res in enumerate(resistors):
                    res_ref = res['reference'].lower()
                    if i == 0:
                        # First resistor connects to power
                        code += f"\n    pwr_net & {res_ref}"
                    else:
                        # Use labels if available for intermediate connections
                        if i-1 < len(labels):
                            div_net = make_valid_identifier(labels[i-1].name)
                            code += f" & {div_net}"
                            code += f"\n    {div_net} & {res_ref}"
                        else:
                            code += f" & {res_ref}"
                
                # Last resistor connects to ground
                code += " & gnd"
            
            # Return appropriate net
            if len(resistors) > 1 and labels:
                div_net = make_valid_identifier(labels[0].name)
                code += f"\n\n    return {div_net}"
            else:
                code += "\n\n    return pwr_net"
        
        else:
            # Generic case for unknown components
            code += "\n    # No specific handling for these components"
            code += "\n    return pwr_net"
    else:
        # Handle case with no components
        code += "\n    # No components found"
        code += "\n    return pwr_net"
    
    return code
