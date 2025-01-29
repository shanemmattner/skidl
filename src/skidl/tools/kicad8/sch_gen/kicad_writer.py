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
            kicad_dir = os.environ.get("KICAD8_SYMBOL_DIR", "/usr/share/kicad/symbols")
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
        Convert a single flattened SymbolDefinition into:
          (symbol "Name"
            (property "Key" "Val" ...)
            (pin "Number" ... ) ...
            ...
          )
        A fully self-contained symbol definition block with no `(extends ...)`.
        """
        lines = []
        lines.append(f"(symbol \"{sym_def.name}\"")

        # Flattened symbol => no extends
        # add properties
        for k, v in sym_def.properties.items():
            lines.append(f"  (property \"{k}\" \"{v}\" (at 0 0 0))")

        # parse out pins list
        # if sym_def.pins is a dict of pin_num => pin def, or a list
        # your code might differ. We'll assume sym_def has a dict or list:
        # e.g. sym_def.pins: Dict[str, PinDefinition]
        # We'll handle each pin
        # let's assume it's dict pin_number => pinDefinition
        if hasattr(sym_def, 'pins') and isinstance(sym_def.pins, dict):
            for p_num, p_def in sym_def.pins.items():
                # minimal approach
                lines.append(f"  (pin \"{p_num}\" ) ; child pin definition placeholder")
        elif hasattr(sym_def, 'pins') and isinstance(sym_def.pins, list):
            # If it's a list, handle similarly
            for p in sym_def.pins:
                # p.number
                # p.name
                lines.append(f"  (pin \"{p.number}\" ) ; minimal pin placeholder")

        # shapes
        for shape in sym_def.shapes:
            lines.append(f"  ; shape: {shape.shape_type}")

        lines.append(")")
        return "\n".join(lines)


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
