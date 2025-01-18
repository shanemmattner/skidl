#!/usr/bin/env python3

import os
import sys
from parsers.sheet_parser import read_schematic_file, extract_sheet_names, extract_sheet_files
from parsers.component_parser import extract_components, extract_hierarchical_labels, generate_skidl_subcircuit

def process_schematic(filepath):
    """Process a KiCad schematic file and generate SKiDL subcircuits."""
    # Read main schematic
    content = read_schematic_file(filepath)
    if not content:
        return False
        
    # Get sheet names and files
    sheet_names = extract_sheet_names(content)
    sheet_files = extract_sheet_files(content)
    
    if not sheet_names or not sheet_files:
        print("No sheets found in schematic")
        return False
    
    print(f"\nFound {len(sheet_names)} sheets:")
    for name, file in zip(sheet_names, sheet_files):
        print(f"- {name}: {file}")
    
    # Create output directory with absolute path
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_subcircuits")
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nCreating output directory: {output_dir}")
    
    # Process each sheet
    base_dir = os.path.dirname(filepath)
    for name, file in zip(sheet_names, sheet_files):
        sheet_path = os.path.join(base_dir, file)
        print(f"\nProcessing sheet: {name}")
        
        # Read sheet content
        sheet_content = read_schematic_file(sheet_path)
        if not sheet_content:
            continue
            
        # Extract components and labels
        components = extract_components(sheet_content)
        labels = extract_hierarchical_labels(sheet_content)
        
        if components:
            print("\nComponents found:")
            for comp in components:
                print(f"- {comp['reference']}: {comp['library']}:{comp['symbol']} ({comp['footprint']})")
        
        if labels:
            print("\nHierarchical labels found:")
            for label in labels:
                print(f"- {label}")
        
        # Generate SKiDL subcircuit
        skidl_code = generate_skidl_subcircuit(name, components, labels)
        
        # Write to file
        output_file = os.path.join(output_dir, f"{name}_subcircuit.py")
        with open(output_file, "w") as f:
            f.write(skidl_code)
            
        print(f"Generated SKiDL subcircuit in '{output_file}'")
    
    # Generate main circuit file
    main_code = """from skidl import *

# Define power nets that will be shared across subcircuits
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

"""
    
    # Import subcircuits
    for name in sheet_names:
        main_code += f"from {name}_subcircuit import {name}\n"
    
    main_code += """
# Instantiate the power nets
vcc_5v = Net('+5V')
vcc_5v.drive = POWER

# Instantiate the subcircuits
"""
    
    # Add subcircuit instantiations
    prev_net = "vcc_5v"
    for i, name in enumerate(sheet_names):
        net_name = f"net_{i}" if i < len(sheet_names)-1 else "final_net"
        main_code += f"{net_name} = {name}({prev_net})\n"
        prev_net = net_name
    
    main_code += "\n# Generate netlist\ngenerate_netlist()"
    
    # Write main circuit
    main_file = os.path.join(output_dir, "main_circuit.py")
    with open(main_file, "w") as f:
        f.write(main_code)
        
    print(f"\nGenerated main circuit in '{main_file}'")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_kicad_sch_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if process_schematic(filepath):
        print("\nSuccessfully processed schematic")
    else:
        print("\nFailed to process schematic")
        sys.exit(1)

if __name__ == "__main__":
    main()
