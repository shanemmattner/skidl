#!/usr/bin/env python3

"""
Enhanced KiCad to SKiDL Converter with Hierarchical Support

This script converts KiCad v8 schematics (.kicad_sch files) into SKiDL Python code.
Features:
- Support for hierarchical designs using subcircuits
- Proper handling of power nets
- Footprint assignments
- Component parameters
- Sheet-to-sheet connections
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, DefaultDict
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime

DEBUG = True

def debug_print(msg: str):
    """Print debug messages if DEBUG is enabled"""
    if DEBUG:
        print(f"DEBUG: {msg}")

@dataclass
class Net:
    """Represents a net in the schematic"""
    name: str
    is_power: bool = False
    pins: List[Tuple[str, str]] = field(default_factory=list)  # List of (component_ref, pin_number)
    sheet_path: str = "/"

@dataclass
class Pin:
    """Represents a pin on a component"""
    number: str
    name: str 
    type: str
    uuid: str
    net: Optional[str] = None

@dataclass
class Part:
    """Represents a component in the schematic"""
    lib_id: str
    reference: str
    value: str
    footprint: Optional[str]
    uuid: str
    unit: int = 1
    on_board: bool = True
    in_bom: bool = True
    sheet_path: str = "/"
    pins: Dict[str, Pin] = field(default_factory=dict)

@dataclass
class Sheet:
    """Represents a hierarchical sheet"""
    name: str
    filename: str
    uuid: str
    sheet_path: str
    pins: Dict[str, str] = field(default_factory=dict)  # pin name -> net name
    input_nets: Set[str] = field(default_factory=set)
    output_nets: Set[str] = field(default_factory=set)
    parts: Dict[str, Part] = field(default_factory=dict)  # UUID -> Part

class KicadSchematicParser:
    """Parser for KiCad schematic files with hierarchical support"""
    
    def __init__(self, filename: str, sheet_path: str = "/"):
        self.filename = filename
        self.sheet_path = sheet_path
        self.parts: Dict[str, Part] = {}  # UUID -> Part
        self.sheets: Dict[str, Sheet] = {}  # UUID -> Sheet
        self.nets: DefaultDict[str, Net] = defaultdict(lambda: Net(""))
        self.power_nets: Set[str] = set()
        debug_print(f"Initializing parser for file: {filename} with sheet_path: {sheet_path}")
        self._parse_file()

    def _parse_pin(self, content: str, part: Part):
        """Parse a pin definition"""
        number_match = re.search(r'\(number "([^"]+)"', content)
        name_match = re.search(r'\(name "([^"]+)"', content)
        type_match = re.search(r'\(type ([^\s\)]+)', content)
        uuid_match = re.search(r'\(uuid ([^\s\)]+)', content)
        
        if number_match and uuid_match:
            pin = Pin(
                number=number_match.group(1),
                name=name_match.group(1) if name_match else '',
                type=type_match.group(1) if type_match else 'passive',
                uuid=uuid_match.group(1)
            )
            part.pins[pin.number] = pin

    def _parse_file(self):
        """Parse the KiCad schematic file"""
        debug_print("Starting schematic file parsing")
        
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                debug_print(f"Successfully read file, content length: {len(content)}")
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return

        # First pass - find power nets
        power_matches = re.finditer(r'\(lib_id "power:[^"]+"', content)
        for match in power_matches:
            lib_id = match.group(0).split('"')[1]
            net_name = lib_id.split(':')[1]
            self.power_nets.add(net_name)
            debug_print(f"Found power net: {net_name}")

        # Second pass - find symbols
        debug_print("Parsing symbol instances...")
        symbol_matches = re.finditer(r'\(symbol\s+.*?^\s*\)', content, re.MULTILINE | re.DOTALL)
        for match in symbol_matches:
            self._parse_symbol(match.group(0))
            
        # Third pass - find sheets and parse them recursively
        debug_print("Parsing hierarchical sheets...")

        sheetname_matches = re.finditer(r'\(property "Sheetname" "([^"]+)"', content)
        sheetfile_matches = re.finditer(r'\(property "Sheetfile" "([^"]+)"', content)
        
        for sheetname_match, sheetfile_match in zip(sheetname_matches, sheetfile_matches):
            sheet_content = sheetname_match.group(0) + sheetfile_match.group(0)
            self._parse_sheet(sheet_content)

        # Fourth pass - parse net connections
        debug_print("Parsing net connections...")
        self._parse_nets(content)

    def _parse_symbol(self, content: str):
        """Parse a symbol (component) instance"""
        # Extract basic component information
        lib_id_match = re.search(r'\(lib_id\s+"([^"]+)"', content)
        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', content)
        value_match = re.search(r'\(property\s+"Value"\s+"([^"]+)"', content)
        uuid_match = re.search(r'\(uuid\s+"([^"]+)"', content)
        footprint_match = re.search(r'\(property\s+"Footprint"\s+"([^"]+)"', content)
        
        if all((lib_id_match, ref_match, uuid_match)):
            lib_id = lib_id_match.group(1)
            reference = ref_match.group(1)
            value = value_match.group(1) if value_match else ''
            footprint = footprint_match.group(1) if footprint_match else None
            uuid = uuid_match.group(1)
            
            debug_print(f"Found part: {reference} ({lib_id}), footprint: {footprint}")
            
            # Skip power symbols but process regular parts
            if not lib_id.startswith("power:"):
                part = Part(
                    lib_id=lib_id,
                    reference=reference,
                    value=value,
                    footprint=footprint,
                    uuid=uuid,
                    sheet_path=self.sheet_path
                )
                
                # Parse pins
                pin_matches = re.finditer(r'\(pin\s+([^\s]+)\s+.*?number\s+"([^"]+)".*?\)', content, re.DOTALL)
                for pin_match in pin_matches:
                    pin_type = pin_match.group(1)
                    pin_num = pin_match.group(2)
                    pin = Pin(
                        number=pin_num,
                        name='',  # Could extract if needed
                        type=pin_type,
                        uuid=uuid
                    )
                    part.pins[pin_num] = pin
                
                self.parts[uuid] = part
                        
    def _parse_sheet(self, content: str):
        """Parse a hierarchical sheet and create subcircuit"""
        debug_print("\nParsing hierarchical sheet...")
        debug_print("Raw sheet content:")
        debug_print(content)
        
        # Extract sheet properties using the new KiCad v8 format
        sheetname_match = re.search(r'\(property "Sheetname" "([^"]+)"', content)
        sheetfile_match = re.search(r'\(property "Sheetfile" "([^"]+)"', content)

        # debug_print("\nRegex patterns:")
        # debug_print(f'Sheetname pattern: property\\s+"Sheetname"\\s+"([^"]+)"')
        # debug_print(f'Sheetfile pattern: property\\s+"Sheetfile"\\s+"([^"]+)"')
        
        debug_print("\nMatches found:")
        debug_print(f"Sheetname match object: {sheetname_match}")
        if sheetname_match:
            debug_print(f"Sheetname groups: {sheetname_match.groups()}")
        debug_print(f"Sheetfile match object: {sheetfile_match}")
        if sheetfile_match:
            debug_print(f"Sheetfile groups: {sheetfile_match.groups()}")

        if not all((sheetname_match, sheetfile_match)):
            debug_print("\nMissing required sheet properties:")
            debug_print(f"Sheetname match: {bool(sheetname_match)}")
            debug_print(f"Sheetfile match: {bool(sheetfile_match)}")
            debug_print("Failed to parse sheet properties - skipping sheet")
            return
            
        name = sheetname_match.group(1)
        filename = sheetfile_match.group(1)
        
        debug_print(f"\nFound hierarchical sheet: {name} ({filename})")

    def generate_subcircuits(self):
        """Generate SKiDL subcircuits from sheets"""
        subcircuit_code = []
        
        for sheet_name, sheet in self.sheets.items():
            # Convert sheet name to valid Python identifier
            func_name = re.sub(r'\W|^(?=\d)', '_', sheet_name.lower())
            
            code = [
                f"\n@subcircuit\n",
                f"def {func_name}("
            ]
            
            # Add input parameters
            params = []
            for pin_name in sorted(sheet.input_nets):
                params.append(pin_name.lower())
            for pin_name in sorted(sheet.output_nets):
                params.append(pin_name.lower())
                
            code.append(", ".join(params))
            code.append("):\n")
            code.append(f'    """{sheet_name} subcircuit"""\n\n')
            
            # Add parts instantiation
            for part in sheet.parts.values():
                code.append(f"    {self._generate_part_instantiation(part, '    ')}\n")
                
            # Add connections
            code.append("\n    # Create connections\n")
            # Add connection code here based on sheet.nets
            
            # Return output nets
            if sheet.output_nets:
                code.append("\n    # Return output nets\n")
                returns = [net.lower() for net in sorted(sheet.output_nets)]
                if len(returns) == 1:
                    code.append(f"    return {returns[0]}\n")
                else:
                    code.append(f"    return {', '.join(returns)}\n")
                    
            subcircuit_code.extend(code)
            
        return "".join(subcircuit_code)                        


    def _parse_sheet_pin(self, content: str, sheet: Sheet):
        """Parse a hierarchical sheet pin"""
        name_match = re.search(r'"([^"]+)"', content)
        net_match = re.search(r'\(net "([^"]+)"', content)
        
        if name_match and net_match:
            pin_name = name_match.group(1)
            net_name = net_match.group(1)
            sheet.pins[pin_name] = net_name

    def _parse_nets(self, content: str):
        """Parse net definitions and connections"""
        # Find power nets
        power_matches = re.finditer(r'\(power.*?\n\s*\)', content, re.DOTALL)
        for match in power_matches:
            net_name_match = re.search(r'"([^"]+)"', match.group(0))
            if net_name_match:
                net_name = net_name_match.group(1)
                self.power_nets.add(net_name)
                self.nets[net_name] = Net(net_name, True)
        
        # Find net connections
        net_matches = re.finditer(r'\(net.*?\n\s*\)', content, re.DOTALL)
        for match in net_matches:
            self._parse_net(match.group(0))

    def _parse_net(self, content: str):
        """Parse a single net definition"""
        name_match = re.search(r'"([^"]+)"', content)
        if not name_match:
            return
            
        net_name = name_match.group(1)
        net = self.nets[net_name]
        
        # Find connected pins
        pin_matches = re.finditer(r'\(pin "([^"]+)" \(ref "([^"]+)"\)', content)
        for pin_match in pin_matches:
            pin_num = pin_match.group(1)
            ref = pin_match.group(2)
            net.pins.append((ref, pin_num))

class SkidlCodeGenerator:
    """Generate SKiDL code from parsed KiCad schematic"""
    
    def __init__(self, parser: KicadSchematicParser):
        self.parser = parser

    def _generate_part_instantiation(self, part: Part, indent: str = "") -> str:
        """Generate code for instantiating a component"""
        # Extract library and part name
        lib_parts = part.lib_id.split(':')
        if len(lib_parts) != 2:
            return f"{indent}# Invalid lib_id: {part.lib_id}\n"
            
        library, part_name = lib_parts
        var_name = part.reference.lower()
        
        # Skip power components
        if library == "power":
            return ""
        
        # Handle basic components with standard naming
        if part_name in ['R', 'C', 'L']:
            code = [f"{indent}{var_name} = Part('Device', '{part_name}'"]
        else:
            code = [f"{indent}{var_name} = Part('{library}', '{part_name}'"]
            
        # Build parameters list
        params = []
        if part.value:
            params.append(f"value='{part.value}'")
        if part.footprint:
            params.append(f"footprint='{part.footprint}'")
            
        if params:
            code.append(", " + ", ".join(params))
            
        code.append(")\n")
        return "".join(code)

    def _generate_subcircuit(self, sheet: Sheet) -> List[str]:
        """Generate a subcircuit for a hierarchical sheet"""
        sheet_name = re.sub(r'\W|^(?=\d)', '_', sheet.name.lower())
        
        code = [
            f"\n@subcircuit\n",
            f"def {sheet_name}(vin):\n",
            f'    """{sheet.name} subcircuit"""\n\n'
        ]
        
        # Generate power nets if needed
        power_nets = [net for net in self.parser.power_nets 
                    if any(p.sheet_path.startswith(sheet.sheet_path) 
                        for p in sheet.parts.values())]
        
        if power_nets:
            code.append("    # Create power nets\n")
            for net_name in power_nets:
                var_name = net_name.lower().replace('+', 'p').replace('-', 'n')
                if var_name not in ('gnd', 'vcc_3v3', 'vcc_5v'):  # Skip globals
                    code.append(f"    {var_name} = Net('{net_name}')\n")
                    code.append(f"    {var_name}.drive = POWER\n")
        
        # Get parts for this sheet
        sheet_parts = [p for p in sheet.parts.values()]
        
        if sheet_parts:
            code.append("\n    # Create components\n")
            for part in sheet_parts:
                inst_code = self._generate_part_instantiation(part, "    ")
                if inst_code:
                    code.append(inst_code)
        
        # Add connections
        code.extend([
            "\n    # Create connections\n",
            self._generate_connections(sheet_parts, sheet, "    ")
        ])
        
        # Return output nets
        if sheet.output_nets:
            code.append("\n    # Return output net\n")
            if len(sheet.output_nets) == 1:
                net_name = list(sheet.output_nets)[0]
                code.append(f"    return {net_name}\n")
            else:
                nets = ", ".join(sheet.output_nets)
                code.append(f"    return {nets}\n")
        else:
            code.append("\n    return locals()\n")
        
        return code

    def generate(self) -> str:
        """Generate complete SKiDL code"""
        debug_print("Starting SKiDL code generation")
        
        # Generate file header and power nets
        code = [
            "from skidl import *\n\n",
            "# Define power nets that will be shared across subcircuits\n",
            "gnd = Net('GND')\n",
            "gnd.drive = POWER\n",
            "gnd.do_erc = False\n\n"
        ]

        # Generate subcircuits from sheets
        for sheet in self.parser.sheets.values():
            code.extend(self._generate_subcircuit(sheet))

        # Generate root level components and connections
        root_parts = [p for p in self.parser.parts.values() 
                    if p.sheet_path == "/" and not p.lib_id.startswith("power:")]
        
        if root_parts:
            code.append("\n# Create root level components\n")
            for part in root_parts:
                code.append(self._generate_part_instantiation(part))
        
        # Create sheet instances
        if self.parser.sheets:
            code.append("\n# Create hierarchical sheets\n")
            for sheet in self.parser.sheets.values():
                sheet_name = re.sub(r'\W|^(?=\d)', '_', sheet.name.lower())
                code.append(f"{sheet_name}_nets = {sheet_name}(vcc_5v)\n")

        # Generate netlist
        code.append("\n# Generate netlist\n")
        code.append("generate_netlist()")
        
        return "".join(code)

    def _generate_connections(self, parts: List[Part], sheet: Sheet, indent: str = "") -> str:
        """Generate connection code for components"""
        code = []
        
        # Build net connectivity map
        net_connections: DefaultDict[str, List[Tuple[str, str]]] = defaultdict(list)
        for part in parts:
            for pin in part.pins.values():
                if pin.net:
                    net_connections[pin.net].append((part.reference.lower(), pin.number))
        
        # Generate connection code
        for net_name, connections in net_connections.items():
            if len(connections) > 1:
                # Create chain of connections
                conn_str = " & ".join([f"{ref}.{pin}" for ref, pin in connections])
                code.append(f"{indent}{conn_str}\n")
        
        return "".join(code)

def convert_kicad_to_skidl(input_file: str, output_file: str):
    """Convert a KiCad schematic to SKiDL code"""
    print(f"Starting conversion of {input_file} to {output_file}")
    
    try:
        # Parse KiCad schematic
        parser = KicadSchematicParser(input_file)
        
        # Generate SKiDL code
        generator = SkidlCodeGenerator(parser)
        skidl_code = generator.generate()
        
        # Write output file
        with open(output_file, 'w') as f:
            f.write(skidl_code)
        
        print(f"Successfully converted {input_file} to {output_file}")
        
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        raise

def process_all_schematics():
    """Process all .kicad_sch files in the current directory"""
    current_dir = Path('.')
    schematic_files = list(current_dir.glob('*.kicad_sch'))
    
    if not schematic_files:
        print("No KiCad schematic files found in current directory")
        return
    
    print(f"Found {len(schematic_files)} schematic files")
    
    for schematic in schematic_files:
        output_file = schematic.stem + '.py'
        print(f"\nProcessing {schematic}")
        try:
            convert_kicad_to_skidl(str(schematic), output_file)
        except Exception as e:
            print(f"Error processing {schematic}: {str(e)}")

def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        # No arguments - process all schematics in current directory
        process_all_schematics()
    elif len(sys.argv) == 3:
        # Process single file with specified output
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        try:
            convert_kicad_to_skidl(input_file, output_file)
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage:")
        print("  Process single file: kicad_to_skidl.py input.kicad_sch output.py")
        print("  Process all files:   kicad_to_skidl.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
