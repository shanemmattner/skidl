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
        self.netlist = parse_netlist(netlist_src)
        self.sheets = {}
        self.tab = " " * 4

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
        for comp in self.netlist.parts:
            # Handle both dict and object property access
            sheet_name = ''
            if isinstance(comp.properties, dict):
                sheet_name = comp.properties.get('Sheetname', '')
            else:
                sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
                sheet_name = sheet_prop.value if sheet_prop else ''
                
            if sheet_name:
                # Find the matching sheet
                for sheet in self.sheets.values():
                    if sheet.name == sheet_name:
                        sheet.components.append(comp)
                        break

    def analyze_nets(self):
        """Analyze nets to determine which are local vs imported for each sheet."""
        print("\n=== Analyzing Nets ===")
        for net in self.netlist.nets:
            net_name = self.legalize_name(net.name)
            
            # Group pins by sheet
            sheet_pins = defaultdict(list)
            for pin in net.pins:
                for comp in self.netlist.parts:
                    if comp.ref == pin.ref:
                        if isinstance(comp.properties, dict):
                            sheet_name = comp.properties.get('Sheetname', '')
                        else:
                            sheet_prop = next((p for p in comp.properties if p.name == 'Sheetname'), None)
                            sheet_name = sheet_prop.value if sheet_prop else ''
                            
                        if sheet_name:
                            sheet_pins[sheet_name].append(pin)
                            break
            
            # Determine if net is local or needs to be imported
            for sheet in self.sheets.values():
                if sheet.name in sheet_pins:
                    if len(sheet_pins.keys()) > 1:
                        sheet.imported_nets.add(net_name)
                    else:
                        sheet.local_nets.add(net_name)

    def component_to_skidl(self, comp: object) -> str:
        """Convert component to SKiDL instantiation."""
        ref = self.legalize_name(comp.ref)
        
        inst = f"{self.tab}{ref} = Part('{comp.lib}', '{comp.name}'"
        
        if comp.value:
            inst += f", value='{comp.value}'"
        if comp.footprint:
            inst += f", footprint='{comp.footprint}'"
            
        inst += ")\n"
        return inst

    def should_include_pin(self, pin, sheet: Sheet) -> bool:
        """Determine if a pin should be included in the output."""
        # Skip unconnected pins
        if 'unconnected' in pin.ref.lower():
            return False
            
        # Skip pins that are only connected to unconnected nets
        if hasattr(pin, 'net') and pin.net and 'unconnected' in pin.net.name.lower():
            return False
            
        # Only include pins for components in this sheet
        return any(comp.ref == pin.ref for comp in sheet.components)

    def net_to_skidl(self, net: object, sheet: Sheet) -> str:
        """Convert net to SKiDL connections for specific sheet."""
        net_name = self.legalize_name(net.name)
        pins = []
        
        for pin in net.pins:
            if self.should_include_pin(pin, sheet):
                comp = self.legalize_name(pin.ref)
                pins.append(f"{comp}['{pin.num}']")
                
        if pins and not net_name.startswith('unconnected_'):
            # Handle special case for D+ and D- nets
            if net_name in ('D_p', 'D_n'):
                return f"{self.tab}{net_name} += {', '.join(pins)}\n"
            return f"{self.tab}{net_name} += {', '.join(pins)}\n"
        return ""

    def legalize_name(self, name: str, is_filename: bool = False) -> str:
        """Convert KiCad names to valid Python identifiers while preserving special cases."""
        # Strip any leading slashes and spaces
        name = name.lstrip('/ ')
        
        # Handle special cases for power nets and differential pairs
        if name == '+3V3':
            return '+3V3'
        if name == '+5V':
            return '+5V'
        if name == 'D+':
            return 'D_p'
        if name == 'D-':
            return 'D_n'
            
        # Replace all non-alphanum/underscore with underscores
        name = re.sub(r'[^a-zA-Z0-9_]+', '_', name)
        
        # Prepend underscore if starts with digit
        if name and name[0].isdigit():
            name = '_' + name
        
        return name

    def convert(self, output_dir: str = None):
        """Convert netlist to SKiDL files."""
        print("\n=== Starting Conversion ===")
        self.extract_sheet_info()
        self.assign_components_to_sheets()
        self.analyze_nets()
        
        if output_dir:
            print(f"\nGenerating files in directory: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate sheet files with correct naming
            for sheet in self.sheets.values():
                sheet_code = self.generate_sheet_code(sheet)
                filename = self.legalize_name(sheet.name, is_filename=True) + '.py'
                sheet_path = Path(output_dir) / filename
                sheet_path.write_text(sheet_code)
                print(f"Wrote sheet file: {sheet_path}")
            
            self.create_main_file(output_dir)
        else:
            print("\nNo output directory specified, returning main sheet code")
            main_sheet = next((s for s in self.sheets.values() if not s.parent), None)
            if main_sheet:
                return self.generate_sheet_code(main_sheet)
            return ""

    # Update generate_sheet_code method to avoid circular imports
    def generate_sheet_code(self, sheet: Sheet) -> str:
        """Generate SKiDL code for a specific sheet."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Only import parent sheets to avoid circular imports
        if sheet.parent:
            parent_sheet = next((s for s in self.sheets.values() if s.path == sheet.parent), None)
            if parent_sheet:
                module_name = self.legalize_name(parent_sheet.name)
                code.append(f"from {module_name} import {module_name}\n")
        
        code.append("\n@subcircuit\n")
        
        # Function definition with proper names
        params = []
        for net in sorted(list(sheet.imported_nets)):
            if not net.startswith('unconnected'):
                params.append(self.legalize_name(net))
        if 'gnd' not in params:
            params.append('gnd')
        
        function_name = self.legalize_name(sheet.name)
        code.append(f"def {function_name}({', '.join(params)}):\n")
        
        # Components
        if sheet.components:
            code.append(f"{self.tab}# Components\n")
            for comp in sorted(sheet.components, key=lambda x: x.ref):
                code.append(self.component_to_skidl(comp))
            code.append("\n")
        
        # Local nets
        local_nets = {net for net in sheet.local_nets if not net.startswith('unconnected')}
        if local_nets:
            code.append(f"{self.tab}# Local nets\n")
            for net in sorted(local_nets):
                code.append(f"{self.tab}{self.legalize_name(net)} = Net('{net}')\n")
            code.append("\n")
        
        # Connections
        code.append(f"{self.tab}# Connections\n")
        for net in self.netlist.nets:
            conn = self.net_to_skidl(net, sheet)
            if conn:
                code.append(conn)
        
        return "".join(code)

    # Update create_main_file method to include all differential pair nets
    def create_main_file(self, output_dir: str):
        """Create the main.py file that ties everything together."""
        code = [
            "# -*- coding: utf-8 -*-\n",
            "from skidl import *\n"
        ]
        
        # Import all sheet modules without main import
        for sheet in self.sheets.values():
            if sheet.name != 'main':
                module_name = self.legalize_name(sheet.name)
                code.append(f"from {module_name} import {module_name}\n")
        
        code.extend([
            "\ndef main():\n",
            f"{self.tab}# Create nets\n",
            f"{self.tab}gnd = Net('GND')\n"
        ])
        
        # Create nets with differential pair handling
        all_nets = set()
        for sheet in self.sheets.values():
            for net in sheet.imported_nets:
                if not net.startswith('unconnected'):
                    all_nets.add(net)
        
        # Add differential pair nets
        if 'D_p' in all_nets or 'D_n' in all_nets:
            all_nets.add('D_p')  # D+
            all_nets.add('D_n')  # D-
        
        for net in sorted(all_nets):
            if net != 'gnd':
                code.append(f"{self.tab}{self.legalize_name(net)} = Net('{net}')\n")
        
        # Call subcircuits in hierarchical order
        code.append(f"\n{self.tab}# Create subcircuits\n")
        sheet_order = self.get_hierarchical_order()
        for sheet in sheet_order:
            if sheet.name != 'main':  # Skip main sheet since we're in it
                params = []
                for net in sorted(list(sheet.imported_nets)):
                    if not net.startswith('unconnected'):
                        params.append(self.legalize_name(net))
                if 'gnd' not in params:
                    params.append('gnd')
                function_name = self.legalize_name(sheet.name)
                code.append(f"{self.tab}{function_name}({', '.join(params)})\n")
        
        code.extend([
            "\nif __name__ == \"__main__\":\n",
            f"{self.tab}main()\n",
            f"{self.tab}generate_netlist()\n"
        ])
        
        main_path = Path(output_dir) / "main.py"
        main_path.write_text("".join(code))
        
    def get_hierarchical_order(self):
        """Return sheets in correct hierarchical order."""
        ordered_sheets = []
        seen = set()
        
        def add_sheet(sheet):
            if sheet.path in seen:
                return
            # Add parent first if it exists
            if sheet.parent and sheet.parent not in seen:
                parent_sheet = next((s for s in self.sheets.values() if s.path == sheet.parent), None)
                if parent_sheet:
                    add_sheet(parent_sheet)
            ordered_sheets.append(sheet)
            seen.add(sheet.path)
        
        # Add sheets in hierarchical order
        for sheet in self.sheets.values():
            add_sheet(sheet)
            
        return ordered_sheets



def netlist_to_skidl(netlist_src: str, output_dir: str = None):
    """Convert a KiCad netlist to SKiDL Python files."""
    print("\n=== Starting Netlist to SKiDL Conversion ===")
    print(f"Input file: {netlist_src}")
    print(f"Output directory: {output_dir}")
    converter = HierarchicalConverter(netlist_src)
    return converter.convert(output_dir)
