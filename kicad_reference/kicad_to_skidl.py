#!/usr/bin/env python3

"""
Enhanced KiCad to SKiDL Converter

This script converts KiCad v8 schematics (.kicad_sch files) into SKiDL Python code.
Added support for:
- Footprint assignments
- Hierarchical schematics using subcircuits
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

DEBUG = True

def debug_print(msg: str):
    """Print debug messages if DEBUG is enabled"""
    if DEBUG:
        print(f"DEBUG: {msg}")

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

@dataclass
class Sheet:
    """Represents a hierarchical sheet"""
    name: str
    filename: str
    uuid: str
    sheet_path: str

class KicadSchematicParser:
    """Parser for KiCad schematic files"""
    
    def __init__(self, filename: str, sheet_path: str = "/"):
        self.filename = filename
        self.sheet_path = sheet_path
        self.parts: Dict[str, Part] = {}  # UUID -> Part
        self.sheets: Dict[str, Sheet] = {}  # UUID -> Sheet
        self.nets: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # Net name -> [(part_ref, pin_num)]
        debug_print(f"Initializing parser for file: {filename} with sheet_path: {sheet_path}")
        self._parse_file()

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

        # Extract symbol instances
        debug_print("Parsing symbol instances...")
        symbol_matches = re.finditer(r'\(symbol.*?\n\s*\)', content, re.DOTALL)
        for match in symbol_matches:
            self._parse_symbol(match.group(0))
            
        # Extract hierarchical sheets
        debug_print("Parsing hierarchical sheets...")
        sheet_matches = re.finditer(r'\(sheet.*?\n\s*\)', content, re.DOTALL)
        for match in sheet_matches:
            self._parse_sheet(match.group(0))

    def _parse_symbol(self, content: str):
        """Parse a symbol instance"""
        # Extract basic information
        lib_id_match = re.search(r'\(lib_id "([^"]+)"', content)
        reference_match = re.search(r'\(property "Reference" "([^"]+)"', content)
        value_match = re.search(r'\(property "Value" "([^"]+)"', content)
        footprint_match = re.search(r'\(property "Footprint" "([^"]+)"', content)
        uuid_match = re.search(r'\(uuid ([^\s\)]+)', content)
        unit_match = re.search(r'\(unit (\d+)\)', content)
        
        if lib_id_match and reference_match and uuid_match:
            lib_id = lib_id_match.group(1)
            reference = reference_match.group(1)
            value = value_match.group(1) if value_match else ''
            footprint = footprint_match.group(1) if footprint_match else None
            uuid = uuid_match.group(1)
            unit = int(unit_match.group(1)) if unit_match else 1
            
            debug_print(f"Found part: {reference} ({lib_id})")
            
            # Create part
            self.parts[uuid] = Part(
                lib_id=lib_id,
                reference=reference,
                value=value,
                footprint=footprint,
                uuid=uuid,
                unit=unit,
                sheet_path=self.sheet_path
            )

    def _parse_sheet(self, content: str):
        """Parse a hierarchical sheet"""
        debug_print("\nParsing hierarchical sheet...")
        name_match = re.search(r'\(property "Sheetname" "([^"]+)"', content)
        filename_match = re.search(r'\(property "Sheetfile" "([^"]+)"', content)
        uuid_match = re.search(r'\(uuid ([^\s\)]+)', content)
        
        debug_print(f"Sheet content: {content[:200]}...")

        if name_match and filename_match and uuid_match:
            name = name_match.group(1)
            filename = filename_match.group(1)
            uuid = uuid_match.group(1)
            sheet_path = f"{self.sheet_path}{uuid}/"
            
            debug_print(f"Found sheet: {name} ({filename})")
            
            # Create sheet
            self.sheets[uuid] = Sheet(
                name=name,
                filename=filename,
                uuid=uuid,
                sheet_path=sheet_path
            )
            
            # Parse the referenced schematic file
            sheet_parser = KicadSchematicParser(filename, sheet_path)
            self.parts.update(sheet_parser.parts)
            self.sheets.update(sheet_parser.sheets)
            self.nets.update(sheet_parser.nets)

class SkidlCodeGenerator:
    """Generate SKiDL code from parsed KiCad schematic"""
    
    def __init__(self, parser: KicadSchematicParser):
        self.parser = parser
        self.sheet_circuits: Dict[str, List[str]] = defaultdict(list)

    def generate(self) -> str:
        """Generate SKiDL code"""
        debug_print("Starting SKiDL code generation")
        
        # Get timestamp and file info
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        code = [
            "from skidl import *\n",
            "from skidl.pyspice import *\n\n",
            f"'''\nGenerated by KiCad to SKiDL converter\n",
            f"Source file: {self.parser.filename}\n",
            f"Generation date: {current_time}\n",
            f"Number of parts: {len(self.parser.parts)}\n",
            f"Number of sheets: {len(self.parser.sheets)}\n'''\n\n"
        ]

        # Group parts by sheet path
        parts_by_sheet = defaultdict(list)
        for part in self.parser.parts.values():
            parts_by_sheet[part.sheet_path].append(part)

        # Generate code for root circuit
        code.extend(self._generate_circuit("/", parts_by_sheet["/"]))

        # Generate subcircuits for sheets
        for sheet in self.parser.sheets.values():
            sheet_parts = parts_by_sheet[sheet.sheet_path]
            if sheet_parts:
                code.extend(self._generate_subcircuit(sheet, sheet_parts))

        result = "".join(code)
        debug_print("Code generation complete")
        return result

    def _generate_circuit(self, sheet_path: str, parts: List[Part]) -> List[str]:
        """Generate circuit code for a sheet"""
        code = []
        
        if sheet_path == "/":
            code.append("# Create default circuit\n")
            code.append("circ = Circuit()\n\n")
        
        if parts:
            code.append("# Instantiate parts\n")
            for part in parts:
                lib_id = part.lib_id.split(':')
                if len(lib_id) == 2:
                    library, part_name = lib_id
                    var_name = part.reference.lower()
                    
                    # Skip power symbols
                    if library == "power":
                        code.append(f"#{var_name} = Part('{library}', '{part_name}', value='{part.value}')\n")
                        continue
                    
                    # Handle special cases for basic components
                    if part_name == 'R':
                        code.append(f"{var_name} = Part('Device', 'R', value='{part.value}')\n")
                    elif part_name == 'C':
                        code.append(f"{var_name} = Part('Device', 'C', value='{part.value}')\n")
                    else:
                        code.append(f"{var_name} = Part('{library}', '{part_name}', value='{part.value}')\n")
                    
                    # Add footprint if available
                    if part.footprint:
                        code.append(f"{var_name}.footprint = '{part.footprint}'\n")
                        
                    debug_print(f"Generated code for part: {part.reference}")
            
            code.append("\n")
        
        return code

    def _generate_subcircuit(self, sheet: Sheet, parts: List[Part]) -> List[str]:
        """Generate subcircuit code for a hierarchical sheet"""
        debug_print(f"\nGenerating subcircuit for sheet: {sheet.name}")
        debug_print(f"Sheet path: {sheet.sheet_path}")
        debug_print(f"Number of parts in sheet: {len(parts)}")
        
        # Create valid Python identifier from sheet name
        sheet_name = re.sub(r'\W|^(?=\d)', '_', sheet.name.lower())
        
        code = [
            f"\n# Subcircuit for sheet: {sheet.name}\n",
            f"@subcircuit\n",
            f"def {sheet_name}():\n",
            f"    '''Sheet: {sheet.name}\n",
            f"    File: {sheet.filename}\n",
            f"    Path: {sheet.sheet_path}'''\n\n"
        ]
        
        # Add parts
        if parts:
            for part in parts:
                lib_id = part.lib_id.split(':')
                if len(lib_id) == 2:
                    library, part_name = lib_id
                    var_name = part.reference.lower()
                    
                    # Skip power symbols
                    if library == "power":
                        code.append(f"    #{var_name} = Part('{library}', '{part_name}', value='{part.value}')\n")
                        continue
                        
                    if part_name == 'R':
                        code.append(f"    {var_name} = Part('Device', 'R', value='{part.value}')\n")
                    elif part_name == 'C':
                        code.append(f"    {var_name} = Part('Device', 'C', value='{part.value}')\n")
                    else:
                        code.append(f"    {var_name} = Part('{library}', '{part_name}', value='{part.value}')\n")
                    
                    if part.footprint:
                        code.append(f"    {var_name}.footprint = '{part.footprint}'\n")

        code.extend([
            "\n",
            "    # Return dict of nets for hierarchical connections\n",
            "    return locals()\n\n"
        ])
        
        return code

def convert_kicad_to_skidl(input_file: str, output_file: str):
    """Convert a KiCad schematic to SKiDL code"""
    print(f"Starting conversion of {input_file} to {output_file}")
    
    # Parse KiCad schematic
    parser = KicadSchematicParser(input_file)
    
    # Generate SKiDL code
    generator = SkidlCodeGenerator(parser)
    skidl_code = generator.generate()
    
    # Write output file
    with open(output_file, 'w') as f:
        f.write(skidl_code)
    
    print(f"Successfully converted {input_file} to {output_file}")

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