# netlist_to_skidl.py

"""
Convert a netlist into an equivalent hierarchical SKiDL program.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set
from kinparse import parse_netlist
from .part import Part
from .net import Net
from .group import SubCircuit

@dataclass
class Sheet:
    name: str
    path: str
    number: str
    components: List
    nets: List
    parent: str = None
    children: List[str] = None

def extract_sheet_hierarchy(netlist_src):
    """Extract sheet hierarchy from netlist."""
    # Parse the netlist if we got a file path or raw content
    if isinstance(netlist_src, (str, bytes)):
        if isinstance(netlist_src, str):
            # It's a file path
            ntlst = parse_netlist(netlist_src)
        else:
            # It's raw content
            ntlst = parse_netlist(netlist_src.decode('utf-8'))
    else:
        # Assume it's already a parsed netlist
        ntlst = netlist_src
        
    # Verify we have a valid parsed netlist
    if not hasattr(ntlst, 'design'):
        raise ValueError("Invalid netlist format - missing design element")
        
    # Ensure we have the proper XML structure
    if not hasattr(ntlst, 'design'):
        raise ValueError(f"Parsed netlist missing design element. Got: {type(ntlst)} with attributes: {dir(ntlst)}")
    if not hasattr(ntlst.design, 'findall'):
        raise ValueError(
            f"Parsed netlist design element missing XML methods. "
            f"Got: {type(ntlst.design)} with attributes: {dir(ntlst.design)}"
        )
        
    # Debug: Print parsed netlist structure
    print("Parsed netlist structure:")
    print(f"Type: {type(ntlst)}")
    print(f"Attributes: {dir(ntlst)}")
    if hasattr(ntlst, 'design'):
        print("\nDesign element:")
        print(f"Type: {type(ntlst.design)}")
        print(f"Attributes: {dir(ntlst.design)}")
        
    sheets = {}
    
    # First pass: Create sheet objects
    for sheet_elem in ntlst.design.findall(".//sheet"):
        number = sheet_elem.find("number").text
        name = sheet_elem.find("name").text.strip("/")
        path = sheet_elem.find("tstamps").text
        
        sheets[path] = Sheet(
            name=name,
            path=path,
            number=number,
            components=[],
            nets=[],
            children=[]
        )
    
    # Second pass: Establish parent-child relationships
    for path, sheet in sheets.items():
        if sheet.number == "1":
            continue
            
        for potential_parent in sheets.values():
            if (sheet.path.startswith(potential_parent.path) and 
                sheet.path != potential_parent.path):
                sheet.parent = potential_parent.path
                potential_parent.children.append(sheet.path)
                break
    
    # Third pass: Assign components to sheets
    for comp in ntlst.components:
        sheet_path = comp.property("Sheetpath").get("tstamps")
        if sheet_path in sheets:
            sheets[sheet_path].components.append(comp)
    
    # Fourth pass: Assign nets to sheets
    for net in ntlst.nets:
        component_sheets = set()
        for pin in net.pins:
            comp_sheet = pin.ref.property("Sheetpath").get("tstamps")
            component_sheets.add(comp_sheet)
        
        ancestor = find_lowest_common_ancestor(component_sheets, sheets)
        if ancestor:
            sheets[ancestor].nets.append(net)
    
    return sheets, ntlst

def find_lowest_common_ancestor(sheet_paths, sheets):
    """Find the lowest common ancestor sheet in the hierarchy."""
    if not sheet_paths:
        return None
    
    current = next(iter(sheet_paths))
    
    while current:
        is_ancestor = True
        for path in sheet_paths:
            if not (path == current or path.startswith(current)):
                is_ancestor = False
                break
        if is_ancestor:
            return current
        current = sheets[current].parent if current in sheets else None
        
    return None

def generate_sheet_module(sheet, output_dir):
    """Generate Python module for a sheet."""
    code = []
    
    code.append("# -*- coding: utf-8 -*-\n")
    code.append("from skidl import *\n")
    
    if sheet.children:
        code.append("# Import child sheets")
        for child in sheet.children:
            module_name = sheet_path_to_module_name(child)
            code.append(f"from . import {module_name}\n")
    
    code.append(f"@SubCircuit")
    code.append(f"def {sheet_path_to_module_name(sheet.path)}(")
    
    interface_nets = get_interface_nets(sheet)
    if interface_nets:
        params = ", ".join(interface_nets)
        code.append(f"    {params}")
    code.append("):")
    
    if sheet.components:
        code.append("\n    # Components")
        for comp in sheet.components:
            code.append(generate_component_code(comp))
    
    if sheet.nets:
        code.append("\n    # Internal nets")
        for net in sheet.nets:
            if is_internal_net(net, sheet):
                code.append(generate_net_code(net))
    
    if sheet.children:
        code.append("\n    # Instantiate child sheets")
        for child in sheet.children:
            child_nets = get_child_interface_nets(child, sheet)
            params = ", ".join(child_nets)
            code.append(f"    {sheet_path_to_module_name(child)}({params})")
    
    return "\n".join(code)

def sheet_path_to_module_name(path):
    """Convert sheet path to valid Python module name."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', path.lower())

def get_interface_nets(sheet):
    """Get nets that cross sheet boundaries."""
    interface_nets = set()
    for net in sheet.nets:
        if not is_internal_net(net, sheet):
            interface_nets.add(net.name)
    return sorted(list(interface_nets))

def is_internal_net(net, sheet):
    """Check if net is entirely internal to the sheet."""
    sheet_path = sheet.path
    for pin in net.pins:
        if pin.ref.property("Sheetpath").get("tstamps") != sheet_path:
            return False
    return True

def get_child_interface_nets(child_path, parent_sheet):
    """Get interface nets needed by child sheet."""
    return ["vdd", "gnd"]  # Placeholder

def generate_component_code(comp):
    """Generate SKiDL code for a component."""
    ref = comp.ref
    lib = comp.lib
    part = comp.name
    code = f"    {ref.lower()} = Part('{lib}', '{part}'"
    
    if hasattr(comp, 'footprint') and comp.footprint:
        code += f", footprint='{comp.footprint}'"
    if hasattr(comp, 'value') and comp.value:
        code += f", value='{comp.value}'"
        
    return code + ")"

def generate_net_code(net):
    """Generate SKiDL code for a net."""
    name = net.name
    pins = [f"{p.ref.lower()}['{p.num}']" for p in net.pins]
    return f"    Net('{name}').connect({', '.join(pins)})"

def create_project_structure(output_dir, sheets, netlist):
    """Create project directory structure and files."""
    project_dir = output_dir / "sheets"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    (project_dir / "__init__.py").touch()
    
    for sheet in sheets.values():
        module_name = sheet_path_to_module_name(sheet.path)
        module_path = project_dir / f"{module_name}.py"
        
        with open(module_path, "w") as f:
            f.write(generate_sheet_module(sheet, project_dir))

def netlist_to_skidl_project(netlist_src, output_dir):
    """Convert netlist to SKiDL project with multiple modules."""
    if isinstance(netlist_src, str):
        # Parse directly from file path
        sheets, netlist = extract_sheet_hierarchy(netlist_src)
    else:
        # Handle already parsed netlist
        sheets, netlist = extract_sheet_hierarchy(netlist_src)
    
    output_path = Path(output_dir)
    create_project_structure(output_path, sheets, netlist)
    print(f"Created SKiDL project in {output_path}")
