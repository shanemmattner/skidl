# -*- coding: utf-8 -*-

# The MIT License (MIT) - Copyright (c) Dave Vandenbout.

"""
Convert a netlist into an equivalent SKiDL program.
"""

import re
import os
from pathlib import Path
from kinparse import parse_netlist

from .part import TEMPLATE
from .utilities import export_to_all


@export_to_all
def netlist_to_skidl(netlist_src, output_dir=None):
    tab = " " * 4

    def legalize(name):
        """Make a string into a legal python variable name."""
        return re.sub("[^a-zA-Z0-9_]", "_", name.lower())  # Made lowercase for consistency

    def extract_sheet_name(source_path):
        """Extract clean sheet name from source path."""
        base = os.path.basename(source_path)
        name = os.path.splitext(base)[0]
        return legalize(name)

    def get_unique_nets(ntlst):
        """Extract unique net names for parameters, excluding GND."""
        nets = set()
        for net in ntlst.nets:
            name = net.name.lstrip('/').lower()
            if name != 'gnd':  # GND is always included by default
                nets.add(name)
        return sorted(list(nets))

    def comp_to_skidl(comp):
        """Convert component to SKiDL instantiation."""
        ltab = tab
        ref = comp.ref.lower()  # Made lowercase for consistency
        
        # Build the component instantiation
        inst = f"{ltab}{ref} = Part('{comp.lib}', '{comp.name}'"
        
        if len(comp.value):
            inst += f", value='{comp.value}'"
        if len(comp.footprint):
            inst += f", footprint='{comp.footprint}'"
            
        inst += ")\n"
        return inst

    def net_to_skidl(net):
        """Convert net to SKiDL connections using += operator."""
        ltab = tab
        net_name = net.name.lstrip('/').lower()  # Convert to lowercase for consistency
        
        # Build list of pins
        pins = []
        for pin in net.pins:
            comp = legalize(pin.ref)  # Name of Python variable storing component
            pin_num = pin.num  # Pin number of component attached to net
            pins.append(f"{comp}['{pin_num}']")
            
        # If there are pins to connect
        if pins:
            pin_list = ", ".join(pins)
            return f"{ltab}{net_name} += {pin_list}\n"
        return ""

    def create_subcircuit_file(sheet_name, content, output_dir):
        """Create a Python file for the subcircuit."""
        file_path = Path(output_dir) / f"{sheet_name}.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        
    def create_main_file(sheet_name, output_dir):
        """Create the main.py file that imports and calls the subcircuit."""
        main_content = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n",
            f"from {sheet_name} import {sheet_name}\n\n",
            "def create_circuit():\n",
            f"{tab}# Create nets\n",
            f"{tab}gnd = Net('GND')\n",
            f"{tab}vin = Net('VIN')\n",
            f"{tab}vout = Net('VOUT')\n\n",
            f"{tab}# Instantiate subcircuit\n",
            f"{tab}{sheet_name}(vin=vin, vout=vout, gnd=gnd)\n\n",
            'if __name__ == "__main__":\n',
            f"{tab}create_circuit()\n",
            f"{tab}generate_netlist()\n"
        ]
        
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(main_content))

    # Parse the netlist
    ntlst = parse_netlist(netlist_src)
    
    # Generate clean sheet name
    sheet_name = extract_sheet_name(ntlst.source)
    
    # Get unique nets for parameters
    net_params = get_unique_nets(ntlst)
    param_list = ", ".join(net_params + ["gnd"])

    # Create the subcircuit content
    skidl = []
    
    # Add header
    skidl.extend([
        "# -*- coding: utf-8 -*-\n",
        "from skidl import *\n\n\n",
        "@subcircuit\n",
        f"def {sheet_name}({param_list}):\n",
        f"{tab}# Components\n"
    ])

    # Add component instantiations (sorted for consistency)
    comp_statements = sorted([comp_to_skidl(c) for c in ntlst.parts])
    skidl.extend(comp_statements)

    # Add net connections section
    skidl.extend([
        f"\n{tab}# Connections\n"
    ])
    
    # Add net connections (sorted for consistency)
    net_statements = sorted([net_to_skidl(n) for n in ntlst.nets])
    skidl.extend([stmt for stmt in net_statements if stmt])  # Filter empty statements

    # If output_dir is specified, create the file structure
    if output_dir:
        # Create the directory structure
        os.makedirs(output_dir, exist_ok=True)
        
        # Create the subcircuit file
        create_subcircuit_file(sheet_name, "".join(skidl), output_dir)
        
        # Create main.py
        create_main_file(sheet_name, output_dir)
        
        return None  # Return None since files are written directly
    
    return "".join(skidl)  # Return content if no output_dir specified