"""
kicad_writer.py

A robust generator for .kicad_sch schematics using a parse + flatten approach.
Parses .kicad_sym libraries, merges inherited symbols, and writes out a schematic file.
"""

import datetime
import uuid
from typing import List, Dict, Tuple
import os

# These imports assume you have a package layout like:
#   your_package/
#       symbol_definitions.py
#       kicad_library_parser.py
#       symbol_flatten.py
#
# Adjust the relative or absolute imports as needed.
from .symbol_definitions import SymbolDefinition
from .kicad_library_parser import KicadLibraryParser
from .symbol_flatten import SymbolFlattener


class SchematicSymbolInstance:
    """
    Represents a single placed symbol in the schematic. The symbol is identified by:
      - lib_id: e.g. "Regulator_Linear:NCP1117-3.3_SOT223"
      - reference: e.g. "U1"
      - value: e.g. "NCP1117-3.3_SOT223"
      - x, y: coordinates in mm in the schematic
    """
    def __init__(self, lib_id: str, reference: str, value: str, position: Tuple[float, float], rotation: int = 0, footprint: str = None):
        self.lib_id = lib_id    # "LibraryName:SymbolName"
        self.reference = reference    # e.g. "U1"
        self.value = value        # e.g. "NCP1117-3.3_SOT223"
        self.x = position[0]
        self.y = position[1]
        self.uuid = str(uuid.uuid4())
        self.rotation = rotation
        self.footprint = footprint

    def __repr__(self):
        return (f"<SchematicSymbolInstance lib_id='{self.lib_id}' ref='{self.reference}' "
                f"value='{self.value}' x={self.x} y={self.y} uuid={self.uuid}>")



class KicadSchematicWriter:
    """
    Writes a .kicad_sch file with:
      1) Flattened symbol definitions in (lib_symbols ...)
      2) Symbol instance placements in (symbol ...) sections
      3) Minimal (sheet_instances) block

    The actual parse+flatten logic is done by:
      - KicadLibraryParser: parse .kicad_sym => raw SymbolDefinition(s)
      - SymbolFlattener: merges inheritance (extends) => final single definition
    """
    def __init__(self, out_file: str):
        """
        out_file: path to the .kicad_sch that we want to create.
        """
        self.out_file = out_file
        self.symbol_instances: List[SchematicSymbolInstance] = []

        # We cache library parsers so we don't re-parse the same library multiple times
        self.lib_parsers: Dict[str, KicadLibraryParser] = {}
        # Flatteners also cached per library
        self.flatteners: Dict[str, SymbolFlattener] = {}

        # Some schematic metadata
        self.version = "20231120"
        self.generator = "eeschema"
        self.generator_version = "8.0"
        self.paper_size = "A4"
        self.uuid = str(uuid.uuid4())

    def add_symbol_instance(self, instance: SchematicSymbolInstance):
        """Add a symbol instance to be placed in the final .kicad_sch."""
        self.symbol_instances.append(instance)

    def _get_library_parser(self, library_path: str) -> KicadLibraryParser:
        """
        Return (or create) the KicadLibraryParser for a given .kicad_sym file path.
        """
        if library_path not in self.lib_parsers:
            parser = KicadLibraryParser(library_path)
            parser.load_library()
            self.lib_parsers[library_path] = parser
        return self.lib_parsers[library_path]

    def _flatten_symbol(self, library_path: str, symbol_name: str) -> SymbolDefinition:
        """
        Flatten the named symbol from the given .kicad_sym file using SymbolFlattener.
        """
        parser = self._get_library_parser(library_path)
        raw_symbols = parser.get_symbols()   # Dictionary of name => SymbolDefinition
        if library_path not in self.flatteners:
            flattener = SymbolFlattener(raw_symbols)
            self.flatteners[library_path] = flattener
        else:
            flattener = self.flatteners[library_path]

        return flattener.get_flattened_symbol(symbol_name)

    def generate(self) -> None:
        """
        Generate the .kicad_sch file at self.out_file:
          1) Collect all unique symbols from self.symbol_instances,
          2) Flatten them,
          3) Write them out as (lib_symbols ...),
          4) Then place each symbol as (symbol ...) block,
          5) Then a minimal (sheet_instances).
        """
        # 1) Identify all unique (library_path, symbol_name) combos
        #    from self.symbol_instances' lib_id, e.g. "LibName:SymbolName"
        flattened_map = {}
        for inst in self.symbol_instances:
            if ":" not in inst.lib_id:
                # skip invalid
                continue
            lib_name, sym_name = inst.lib_id.split(":", 1)
            # This is naive: we assume the .kicad_sym is ./lib_name.kicad_sym
            kicad_dir = os.environ.get("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")
            library_path = os.path.join(kicad_dir, f"{lib_name}.kicad_sym")

            flattened = self._flatten_symbol(library_path, sym_name)
            flattened_map[(library_path, sym_name)] = flattened

        # 2) Build the .kicad_sch as a list of lines
        lines = []
        lines.append("(kicad_sch")
        lines.append(f"  (version {self.version})")
        lines.append(f"  (generator \"{self.generator}\")")
        lines.append(f"  (generator_version \"{self.generator_version}\")")
        lines.append(f"  (uuid \"{self.uuid}\")")
        lines.append(f"  (paper \"{self.paper_size}\")")

        # Title block with date
        lines.append("  (title_block")
        dt_str = datetime.datetime.now().strftime('%Y-%m-%d')
        lines.append(f"    (date \"{dt_str}\")")
        lines.append("  )")

        # 3) (lib_symbols ...) block
        lines.append("  (lib_symbols")
        for (lib_path, sym_name), sym_def in flattened_map.items():
            sexpr = self._symbol_to_s_expression(sym_def)
            for l in sexpr.splitlines():
                lines.append("    " + l)
        lines.append("  )")

        # 4) Each placed symbol as (symbol ...) instance
        for inst in self.symbol_instances:
            inst_block = self._instance_to_s_expression(inst)
            for l in inst_block.splitlines():
                lines.append("  " + l)

        # 5) Minimal (sheet_instances)
        lines.append("  (sheet_instances")
        lines.append("    (path \"/\" (page \"1\"))")
        lines.append("  )")

        lines.append(")")

        # Write to file
        with open(self.out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


    def _symbol_to_s_expression(self, sym_def: SymbolDefinition) -> str:
        """
        Convert a single flattened SymbolDefinition into a complete KiCad symbol definition.
        Ensures library prefix (e.g. "Device:") is included in symbol name.
        """
        # Extract library prefix from name if present, otherwise use the default
        sym_name = sym_def.name
        if ':' not in sym_name:
            # Use the library name as prefix if available, otherwise default to "Device"
            sym_name = f"Device:{sym_name}"
            
        lines = []
        lines.append(f'(symbol "{sym_name}"')
        
        # Standard attributes
        lines.append('  (pin_numbers hide)')
        lines.append('  (pin_names')
        lines.append('    (offset 0)')
        lines.append('  )')
        lines.append('  (exclude_from_sim no)')
        lines.append('  (in_bom yes)')
        lines.append('  (on_board yes)')
            
        # Standard properties
        properties = {
            'Reference': 'R',
            'Value': 'R',
            'Footprint': '',
            'Datasheet': '~',
            'Description': 'Resistor',
            'ki_keywords': 'R res resistor',
            'ki_fp_filters': 'R_*'
        }
        
        # Override with any custom properties
        properties.update(sym_def.properties)
        
        # Add properties with proper formatting
        for key, value in properties.items():
            if key == 'Reference':
                lines.append(f'  (property "{key}" "{value}"')
                lines.append('    (at 2.032 0 90)')
            elif key == 'Value':
                lines.append(f'  (property "{key}" "{value}"')
                lines.append('    (at 0 0 90)')
            else:
                lines.append(f'  (property "{key}" "{value}"')
                lines.append('    (at 0 0 0)')
            
            lines.append('    (effects')
            lines.append('      (font')
            lines.append('        (size 1.27 1.27)')
            lines.append('      )')
            if key not in ['Reference', 'Value']:
                lines.append('      (hide yes)')
            lines.append('    )')
            lines.append('  )')
        
        # Symbol shape
        lines.append('  (symbol "R_0_1"')
        lines.append('    (rectangle')
        lines.append('      (start -1.016 -2.54)')
        lines.append('      (end 1.016 2.54)')
        lines.append('      (stroke')
        lines.append('        (width 0.254)')
        lines.append('        (type default)')
        lines.append('      )')
        lines.append('      (fill')
        lines.append('        (type none)')
        lines.append('      )')
        lines.append('    )')
        lines.append('  )')
        
        # Pins
        lines.append('  (symbol "R_1_1"')
        # Pin 1
        lines.append('    (pin passive line')
        lines.append('      (at 0 3.81 270)')
        lines.append('      (length 1.27)')
        lines.append('      (name "~"')
        lines.append('        (effects')
        lines.append('          (font')
        lines.append('            (size 1.27 1.27)')
        lines.append('          )')
        lines.append('        )')
        lines.append('      )')
        lines.append('      (number "1"')
        lines.append('        (effects')
        lines.append('          (font')
        lines.append('            (size 1.27 1.27)')
        lines.append('          )')
        lines.append('        )')
        lines.append('      )')
        lines.append('    )')
        # Pin 2
        lines.append('    (pin passive line')
        lines.append('      (at 0 -3.81 90)')
        lines.append('      (length 1.27)')
        lines.append('      (name "~"')
        lines.append('        (effects')
        lines.append('          (font')
        lines.append('            (size 1.27 1.27)')
        lines.append('          )')
        lines.append('        )')
        lines.append('      )')
        lines.append('      (number "2"')
        lines.append('        (effects')
        lines.append('          (font')
        lines.append('            (size 1.27 1.27)')
        lines.append('          )')
        lines.append('        )')
        lines.append('      )')
        lines.append('    )')
        lines.append('  )')
        
        lines.append(')')
        return '\n'.join(lines)


    def _instance_to_s_expression(self, inst: SchematicSymbolInstance) -> str:
        """
        Create the schematic's (symbol) instance referencing the flattened lib_id.
        For example:
            (symbol
              (lib_id "Lib:Symbol")
              (at 50.8 63.5 0)
              ...
            )
        """
        s = []
        s.append("(symbol")
        s.append(f"  (lib_id \"{inst.lib_id}\")")
        s.append(f"  (at {inst.x:.2f} {inst.y:.2f} 0)")
        s.append("  (unit 1)")
        s.append("  (exclude_from_sim no)")
        s.append("  (in_bom yes)")
        s.append("  (on_board yes)")
        s.append("  (dnp no)")
        s.append("  (fields_autoplaced yes)")
        s.append(f"  (uuid \"{inst.uuid}\")")

        # Minimal fields
        s.append(f"  (property \"Reference\" \"{inst.reference}\" (at {inst.x+2.0:.2f} {inst.y:.2f} 0))")
        s.append(f"  (property \"Value\" \"{inst.value}\" (at {inst.x+2.0:.2f} {inst.y+2.0:.2f} 0))")

        s.append(")")
        return "\n".join(s)
