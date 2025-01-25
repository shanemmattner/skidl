# -*- coding: utf-8 -*-

"""
Convert a KiCad netlist into equivalent hierarchical SKiDL programs.
"""

import re
import os
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set
from kinparse import parse_netlist

@dataclass
class Sheet:
    number: str
    name: str
    path: str
    components: List
    local_nets: Set[str]
    imported_nets: Set[str]
    parent: str = None

class HierarchicalConverter:
    def __init__(self, netlist_src):
        print("\n=== Initializing Converter ===")
        self.netlist = parse_netlist(netlist_src)
        print(f"Found {len(self.netlist.parts)} components")
        print(f"Found {len(self.netlist.nets)} nets")
        print(f"Found {len(self.netlist.sheets)} sheets")
        self.sheets = {}  # sheet_path -> Sheet
        self.tab = " " * 4
        
    def legalize_name(self, name: str) -> str:
        """Convert KiCad names to valid Python identifiers."""
        # Handle power nets
        if name.startswith('+'):
            return f"net_{name.lstrip('+').lower()}"
        # Handle hierarchical paths
        name = name.lstrip('/')
        # Replace non-alphanumeric with underscore
        return re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    
    def extract_sheet_info(self):
        """Build sheet hierarchy from netlist."""
        print("\n=== Extracting Sheet Info ===")
        for sheet in self.netlist.sheets:
            print(f"\nProcessing sheet: {sheet.name}")
            path = sheet.name.strip('/')
            name = path.split('/')[-1] if path else 'main'
            parent = '/'.join(path.split('/')[:-1]) if '/' in path else None
            print(f"  Path: {path}")
            print(f"  Name: {name}")
            print(f"  Parent: {parent}")
            
            self.sheets[path] = Sheet(
                number=sheet.number,
                name=name,
                path=path,
                components=[],
                local_nets=set(),
                imported_nets=set(),
                parent=parent
            )
    
    def assign_components_to_sheets(self):
        """Assign components to their respective sheets."""
        print("\n=== Assigning Components to Sheets ===")
        for i, comp in enumerate(self.netlist.parts):
            print(f"\nComponent {i+1}: {comp.ref}")
            print(f"  Properties type: {type(comp.properties)}")
            print(f"  Properties content: {comp.properties}")
            
            if isinstance(comp.properties, dict):
                sheet_name = comp.properties.get('Sheetname', '')
                print(f"  Dict access - Sheet name: {sheet_name}")
            else:
                # Handle case where properties might be objects
                print("  Looking for Sheetname in properties...")
                for prop in comp.properties:
                    print(f"    Property: {prop.name} = {prop.value if hasattr(prop, 'value') else 'NO_VALUE'}")
                sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
                sheet_name = sheet_prop.value if sheet_prop else ''
                print(f"  Object access - Sheet name: {sheet_name}")
                
            if sheet_name:
                print(f"  Found sheet name: {sheet_name}")
                # Find the matching sheet
                for sheet in self.sheets.values():
                    if sheet.name == sheet_name:
                        sheet.components.append(comp)
                        print(f"  Assigned to sheet: {sheet.name}")
                        break
            else:
                print("  No sheet name found!")

    def analyze_nets(self):
        """Analyze nets to determine which are local vs imported for each sheet."""
        print("\n=== Analyzing Nets ===")
        for i, net in enumerate(self.netlist.nets):
            print(f"\nAnalyzing net {i+1}: {net.name}")
            net_name = self.legalize_name(net.name)
            print(f"  Legalized name: {net_name}")
            
            # Group pins by sheet
            sheet_pins = defaultdict(list)
            for pin in net.pins:
                print(f"\n  Processing pin: {pin.ref}.{pin.num}")
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        print(f"    Found component: {comp.ref}")
                        print(f"    Properties type: {type(comp.properties)}")
                        
                        # Use the same property access pattern as assign_components_to_sheets
                        if isinstance(comp.properties, dict):
                            sheet_name = comp.properties.get('Sheetname', '')
                            print(f"    Dict access - Sheet name: {sheet_name}")
                        else:
                            sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
                            sheet_name = sheet_prop.value if sheet_prop else ''
                            print(f"    Object access - Sheet name: {sheet_name}")
                            
                        if sheet_name:
                            sheet_pins[sheet_name].append(pin)
                            print(f"    Added pin to sheet: {sheet_name}")
                            break
            
            print(f"\n  Pin distribution across sheets: {dict(sheet_pins)}")
            
            # Determine if net is local or needs to be imported
            for sheet in self.sheets.values():
                if sheet.name in sheet_pins:
                    if len(sheet_pins.keys()) > 1:
                        sheet.imported_nets.add(net_name)
                        print(f"  Added as imported net to sheet: {sheet.name}")
                    else:
                        sheet.local_nets.add(net_name)
                        print(f"  Added as local net to sheet: {sheet.name}")

    def component_to_skidl(self, comp: object) -> str:
        """Convert component to SKiDL instantiation."""
        print(f"\nConverting component to SKiDL: {comp.ref}")
        ref = self.legalize_name(comp.ref)
        
        inst = f"{self.tab}{ref} = Part('{comp.lib}', '{comp.name}'"
        
        if comp.value:
            inst += f", value='{comp.value}'"
        if comp.footprint:
            inst += f", footprint='{comp.footprint}'"
            
        inst += ")\n"
        print(f"Generated code: {inst.strip()}")
        return inst
    
    def net_to_skidl(self, net: object, sheet: Sheet) -> str:
        """Convert net to SKiDL connections for specific sheet."""
        print(f"\nConverting net to SKiDL: {net.name}")
        net_name = self.legalize_name(net.name)
        pins = []
        
        for pin in net.pins:
            # Only include pins for components in this sheet
            if any(comp.ref == pin.ref for comp in sheet.components):
                comp = self.legalize_name(pin.ref)
                pins.append(f"{comp}['{pin.num}']")
                print(f"  Added pin: {comp}['{pin.num}']")
                
        if pins:
            result = f"{self.tab}{net_name} += {', '.join(pins)}\n"
            print(f"Generated code: {result.strip()}")
            return result
        return ""
    
    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate SKiDL code for a specific sheet."""
        print(f"\n=== Generating Code for Sheet: {sheet.name} ===")
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Add imports from parent/child sheets
        for s in self.sheets.values():
            if s.parent == sheet.path or sheet.parent == s.path:
                code.append(f"from {s.name} import {s.name}\n")
                print(f"Added import: from {s.name} import {s.name}")
        
        code.append("\n@subcircuit\n")
        
        # Function definition with parameters
        params = sorted(list(sheet.imported_nets))
        if 'gnd' not in params:
            params.append('gnd')
        code.append(f"def {sheet.name}({', '.join(params)}):\n")
        print(f"Function definition: def {sheet.name}({', '.join(params)})")
        
        # Local nets
        if sheet.local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in sorted(sheet.local_nets):
                code.append(f"{self.tab}{net} = Net('{net}')\n")
                print(f"Added local net: {net}")
            code.append("\n")
        
        # Components
        if sheet.components:
            code.append(f"{self.tab}# Components\n")
            for comp in sorted(sheet.components, key=lambda x: x.ref):
                code.append(self.component_to_skidl(comp))
            code.append("\n")
        
        # Connections
        code.append(f"{self.tab}# Connections\n")
        for net in self.netlist.nets:
            conn = self.net_to_skidl(net, sheet)
            if conn:
                code.append(conn)
        
        return "".join(code)
    
    def create_main_file(self, output_dir: str):
        """Create the main.py file that ties everything together."""
        print("\n=== Creating Main File ===")
        main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
        if not main_sheet:
            print("No main sheet found!")
            return
        
        print(f"Found main sheet: {main_sheet.name}")
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n",
            f"from {main_sheet.name} import {main_sheet.name}\n\n",
            "def create_circuit():\n",
            f"{self.tab}# Create nets\n",
            f"{self.tab}gnd = Net('GND')\n"
        ]
        
        # Create nets for main sheet parameters
        for net in sorted(main_sheet.imported_nets):
            if net != 'gnd':
                code.append(f"{self.tab}{net} = Net('{net}')\n")
                print(f"Added net: {net}")
        
        code.extend([
            f"\n{self.tab}# Instantiate main circuit\n",
            f"{self.tab}{main_sheet.name}({', '.join(sorted(list(main_sheet.imported_nets)))})\n\n",
            'if __name__ == "__main__":\n',
            f"{self.tab}create_circuit()\n",
            f"{self.tab}generate_netlist()\n"
        ])
        
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(code))
        print(f"Wrote main file to: {main_path}")
    
    def convert(self, output_dir: str = None):
        """Convert netlist to SKiDL files."""
        print("\n=== Starting Conversion ===")
        # Extract and analyze circuit structure
        self.extract_sheet_info()
        self.assign_components_to_sheets()
        self.analyze_nets()
        
        if output_dir:
            print(f"\nGenerating files in directory: {output_dir}")
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate sheet files
            for sheet in self.sheets.values():
                sheet_code = self.generate_sheet_code(sheet)
                sheet_path = Path(output_dir) / f"{sheet.name}.py"
                sheet_path.write_text(sheet_code)
                print(f"Wrote sheet file: {sheet_path}")
            
            # Generate main.py
            self.create_main_file(output_dir)
        else:
            print("\nNo output directory specified, returning main sheet code")
            # Return main sheet code if no output directory specified
            main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
            if main_sheet:
                return self.generate_sheet_code(main_sheet)
            return ""

def netlist_to_skidl(netlist_src: str, output_dir: str = None):
    """Convert a KiCad netlist to SKiDL Python files."""
    print("\n=== Starting Netlist to SKiDL Conversion ===")
    print(f"Input file: {netlist_src}")
    print(f"Output directory: {output_dir}")
    converter = HierarchicalConverter(netlist_src)
    return converter.convert(output_dir)