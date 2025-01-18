"""Main schematic processing logic."""

import os
from typing import List, Optional, Dict
from dataclasses import dataclass
from .parsers.base_parser import KiCadSchematicParser, Sheet
from .generators.base_generator import SKiDLGenerator, CircuitConfig
from .config import DEFAULT_CONFIG

@dataclass
class ProcessingResult:
    """Result of schematic processing."""
    success: bool
    message: str
    generated_files: List[str]

class SchematicProcessor:
    """Handles the processing of schematics into SKiDL code."""
    
    def __init__(self, config: Optional[dict] = None):
        self.config = CircuitConfig(
            power_nets=config.get('power_nets', DEFAULT_CONFIG['power_nets']) if config else DEFAULT_CONFIG['power_nets'],
            default_values=config.get('default_values', DEFAULT_CONFIG['default_values']) if config else DEFAULT_CONFIG['default_values']
        )
        self.parser = KiCadSchematicParser()
        self.generator = SKiDLGenerator(self.config)
        
    def process_schematic(self, filepath: str, output_dir: str) -> ProcessingResult:
        """Process a KiCad schematic file and generate SKiDL subcircuits."""
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Read and parse main schematic
            with open(filepath, 'r') as f:
                content = f.read()
                
            if not content:
                return ProcessingResult(
                    success=False,
                    message=f"Failed to read schematic file: {filepath}",
                    generated_files=[]
                )
            
            # Parse sheets
            sheets = self._parse_sheets(content, os.path.dirname(filepath))
            if not sheets:
                return ProcessingResult(
                    success=False,
                    message="No valid sheets found in schematic",
                    generated_files=[]
                )
            
            # Generate subcircuits
            generated_files = []
            for sheet in sheets:
                output_file = os.path.join(output_dir, f"{sheet.name}_subcircuit.py")
                skidl_code = self.generator.generate_subcircuit(sheet)
                
                with open(output_file, "w") as f:
                    f.write(skidl_code)
                generated_files.append(output_file)
            
            # Generate main circuit
            main_file = self._generate_main_circuit(sheets, output_dir)
            generated_files.append(main_file)
            
            return ProcessingResult(
                success=True,
                message=f"Successfully generated {len(generated_files)} files",
                generated_files=generated_files
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error processing schematic: {str(e)}",
                generated_files=[]
            )
    
    def _parse_sheets(self, content: str, base_dir: str) -> List[Sheet]:
        """Parse all sheets in the schematic."""
        sheets = []
        
        # Parse main sheet first
        main_sheet = self.parser.parse_sheet(content)
        if main_sheet:
            sheets.append(main_sheet)
        
        # Parse subsheets
        for sheet in sheets[:]:  # Copy list to allow modification during iteration
            sheet_path = os.path.join(base_dir, sheet.file_path)
            try:
                with open(sheet_path, 'r') as f:
                    sheet_content = f.read()
                    sub_sheet = self.parser.parse_sheet(sheet_content)
                    if sub_sheet:
                        sheets.append(sub_sheet)
            except Exception as e:
                print(f"Warning: Failed to parse sheet {sheet_path}: {e}")
                
        return sheets
    
    def _generate_main_circuit(self, sheets: List[Sheet], output_dir: str) -> str:
        """Generate the main circuit file that imports and connects all subcircuits."""
        code = [
            "from skidl import *",
            "",
            "# Define power nets",
            "gnd = Net('GND')",
            "gnd.drive = POWER",
            "gnd.do_erc = False",
            "",
            "vcc_5v = Net('+5V')",
            "vcc_5v.drive = POWER",
            ""
        ]
        
        # Import subcircuits
        for sheet in sheets:
            code.append(f"from {sheet.name}_subcircuit import {sheet.name}")
        
        code.extend([
            "",
            "# Instantiate subcircuits"
        ])
        
        # Add subcircuit instantiations
        prev_net = "vcc_5v"
        for i, sheet in enumerate(sheets):
            net_name = f"net_{i}" if i < len(sheets)-1 else "final_net"
            code.append(f"{net_name} = {sheet.name}({prev_net})")
            prev_net = net_name
        
        code.extend([
            "",
            "# Generate netlist",
            "generate_netlist()"
        ])
        
        # Write main circuit file
        main_file = os.path.join(output_dir, "main_circuit.py")
        with open(main_file, "w") as f:
            f.write("\n".join(code))
            
        return main_file
