#!/usr/bin/env python3
"""
kicad_writer.py

Creates a .kicad_sch with flattened library symbols. Each symbol
inherits from its parent (extends "X") fully, then we re-indent
the output so KiCad can parse it properly.

Depends on an external SymbolParser for reading `.kicad_sym` libraries:
   from .symbol_parser import SymbolParser, SymbolDefinition, Pin
"""

import os
import uuid
import datetime
from typing import List, Optional, Dict, Set, Tuple

# ---------------------------------------------------------------------------
# Here is a minimal inline SymbolParser to illustrate the parse+flatten logic.
# If you already have symbol_parser.py, you can import from that instead.
# ---------------------------------------------------------------------------

from dataclasses import dataclass, field


@dataclass
class Pin:
    number: str
    name: Optional[str] = None


@dataclass
class SymbolDefinition:
    name: str
    extends: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    pins: List[Pin] = field(default_factory=list)
    raw_shapes: List[str] = field(default_factory=list)
    is_flattened: bool = False


class SymbolParser:
    def __init__(self, libfile: str):
        self.libfile = libfile
        self.loaded = False
        self.symbols: Dict[str, SymbolDefinition] = {}

    def load_library(self):
        if self.loaded:
            return
        if not os.path.isfile(self.libfile):
            raise FileNotFoundError(f"Library file not found: {self.libfile}")
        with open(self.libfile, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        i = 0
        n = len(all_lines)
        while i < n:
            line = all_lines[i].strip()
            if line.startswith("(symbol "):
                block, i = self._collect_block(all_lines, i)
                sdef = self._parse_symbol_block(block)
                self.symbols[sdef.name] = sdef
            else:
                i += 1

        self.loaded = True

    def _collect_block(self, lines, start_idx):
        block = []
        bracket_depth = 0
        i = start_idx
        while i < len(lines):
            l = lines[i]
            block.append(l)
            bracket_depth += l.count("(")
            bracket_depth -= l.count(")")
            i += 1
            if bracket_depth <= 0:
                break
        return block, i

    def _parse_symbol_block(self, sym_lines: List[str]) -> SymbolDefinition:
        raw_text = "\n".join(sym_lines)
        name = None
        extends_name = None
        first_line = sym_lines[0].strip()
        idx = first_line.find("(symbol ")
        if idx >= 0:
            rest = first_line[idx+8:].strip()
            if rest.startswith('"'):
                second_quote = rest.find('"', 1)
                name = rest[1:second_quote]
                after_name = rest[second_quote+1:].strip()
                if "(extends " in after_name:
                    eq = after_name.find("(extends")
                    sub = after_name[eq:]
                    q1 = sub.find('"')
                    q2 = sub.find('"', q1+1)
                    extends_name = sub[q1+1:q2]

        if not name:
            name = "UnknownSymbol"

        sdef = SymbolDefinition(name=name, extends=extends_name)

        # Parse lines for properties, pins, shapes
        for ln in sym_lines:
            ln_str = ln.strip()
            if "(extends " in ln_str:
                continue
            if ln_str.startswith("(property "):
                parts = ln_str.split('"')
                if len(parts) >= 4:
                    pkey = parts[1]
                    pval = parts[3]
                    sdef.properties[pkey] = pval
            elif ln_str.startswith("(pin "):
                pparts = ln_str.split('"')
                if len(pparts) >= 2:
                    pin_num = pparts[1]
                    sdef.pins.append(Pin(number=pin_num))
            elif ln_str.startswith("(symbol "):
                # skip nested sub-block
                pass
            else:
                sdef.raw_shapes.append(ln_str)

        return sdef

    def get_flattened_symbol(self, sym_name: str) -> Optional[SymbolDefinition]:
        self.load_library()
        if sym_name not in self.symbols:
            return None
        return self._flatten_symbol(sym_name, visited=set())

    def _flatten_symbol(self, sym_name: str, visited: Set[str]) -> SymbolDefinition:
        if sym_name in visited:
            raise ValueError(f"Cycle extends in {sym_name}")
        visited.add(sym_name)
        sym_def = self.symbols[sym_name]
        if sym_def.is_flattened:
            return sym_def
        if sym_def.extends:
            pdef = self._flatten_symbol(sym_def.extends, visited)
            self._merge_symbol_defs(pdef, sym_def)
        sym_def.is_flattened = True
        return sym_def

    def _merge_symbol_defs(self, parent: SymbolDefinition, child: SymbolDefinition):
        for k,v in parent.properties.items():
            if k not in child.properties:
                child.properties[k] = v
        child_pin_nums = {p.number for p in child.pins}
        for pp in parent.pins:
            if pp.number not in child_pin_nums:
                child.pins.append(pp)
        # shapes
        child.raw_shapes = parent.raw_shapes + child.raw_shapes
        child.extends = None


###############################################################################
# SchematicSymbol data class
###############################################################################

class SchematicSymbol:
    def __init__(
        self,
        lib_id: str,
        reference: str,
        value: str,
        position: Tuple[float, float] = (63.5, 63.5),
        rotation: float = 0.0,
        unit: int = 1,
        in_bom: bool = True,
        on_board: bool = True,
        footprint: Optional[str] = None,
        pin_numbers_visible: bool = True,
        pin_names_visible: bool = True,
        symbol_uuid: Optional[str] = None
    ):
        self.lib_id = lib_id
        self.reference = reference
        self.value = value
        self.position = position
        self.rotation = rotation
        self.unit = unit
        self.in_bom = in_bom
        self.on_board = on_board
        self.footprint = footprint or ""
        self.pin_numbers_visible = pin_numbers_visible
        self.pin_names_visible = pin_names_visible
        self.uuid = symbol_uuid or str(uuid.uuid4())

###############################################################################
# Final Output Helpers
###############################################################################

def symbol_def_to_sexpr(sym_def: SymbolDefinition) -> str:
    """
    Convert SymbolDefinition -> (symbol ...) text. Then prettify indentation.
    """
    lines = []
    lines.append(f'(symbol "{sym_def.name}"')

    # Properties
    for pname, pval in sym_def.properties.items():
        lines.append(f'  (property "{pname}" "{pval}")')

    # Pins
    for p in sym_def.pins:
        lines.append(f'  (pin "{p.number}")')

    # shapes (raw lines, but we indent them with 2 spaces)
    for shape_ln in sym_def.raw_shapes:
        # shape_ln might be multi-line if the library had multiline definitions
        shape_split = shape_ln.splitlines()
        for sub_ln in shape_split:
            lines.append("  " + sub_ln.strip())

    lines.append(")")
    text = "\n".join(lines)

    # Now run a bracket-based re-indentation pass so KiCad can parse it nicely
    return _prettify_sexpr(text)


def _prettify_sexpr(text: str) -> str:
    """
    Simple bracket-based re-indenter. 
    """
    out_lines = []
    indent = 0
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        # Count parens
        close_count = line.count(")")
        open_count = line.count("(")

        # if there's more ) than ( on this line, reduce indent first
        net = open_count - close_count
        # Some lines might have multiple open/close, so we do:
        # if close_count > open_count, we reduce indent by (close_count - open_count) 
        # *before* writing line
        if close_count > open_count:
            indent -= (close_count - open_count)
            if indent < 0:
                indent = 0

        # write line with current indent
        out_lines.append(("  " * indent) + line)

        # if net > 0, we add indent
        if net > 0:
            indent += net
    return "\n".join(out_lines)


###############################################################################
# The writer class
###############################################################################

class KicadSchematicWriter:
    """
    Writes a .kicad_sch with:
      - Flattened (lib_symbols ...) for each unique symbol lib_id
      - Placed (symbol ...) blocks
      - Minimal sheet_instances
    """

    def __init__(self, kicad_lib_path: str):
        self.symbols: List[SchematicSymbol] = []
        self.version = "20231120"
        self.generator = "eeschema"
        self.generator_version = "8.0"
        self.paper_size = "A4"
        self.uuid = str(uuid.uuid4())

        self.kicad_lib_path = kicad_lib_path
        self._parser_cache: Dict[str, SymbolParser] = {}

    def add_symbol(self, sym: SchematicSymbol):
        self.symbols.append(sym)

    def _find_library_file(self, library_name: str) -> Optional[str]:
        """
        Find <library_name>.kicad_sym in self.kicad_lib_path
        """
        if not os.path.isdir(self.kicad_lib_path):
            return None
        fname = os.path.join(self.kicad_lib_path, f"{library_name}.kicad_sym")
        if os.path.isfile(fname):
            return fname
        return None

    def _get_symbol_parser(self, library_name: str) -> Optional[SymbolParser]:
        if library_name in self._parser_cache:
            return self._parser_cache[library_name]
        lib_file = self._find_library_file(library_name)
        if not lib_file:
            return None
        sp = SymbolParser(lib_file)
        self._parser_cache[library_name] = sp
        return sp

    def _generate_lib_symbols_section(self) -> str:
        lines = []
        lines.append("\t(lib_symbols")
        unique_lids = sorted({sym.lib_id for sym in self.symbols})
        for lid in unique_lids:
            if ":" not in lid:
                # fallback
                lines.append(f"\t\t(symbol \"{lid}\" (property \"Value\" \"???\"))")
                continue
            libname, symname = lid.split(":", 1)
            parser = self._get_symbol_parser(libname)
            if not parser:
                lines.append(f"\t\t(symbol \"{lid}\" (property \"Value\" \"???\"))")
                continue
            sdef = parser.get_flattened_symbol(symname)
            if not sdef:
                lines.append(f"\t\t(symbol \"{lid}\" (property \"Value\" \"???\"))")
                continue
            # Flattened
            flattened = symbol_def_to_sexpr(sdef)
            flines = flattened.splitlines()
            for fl in flines:
                lines.append("\t\t" + fl)
        lines.append("\t)")
        return "\n".join(lines) + "\n"

    def _generate_symbol_instance(self, sym: SchematicSymbol) -> str:
        """
        Minimal placed symbol s-expression
        """
        lines = []
        lines.append("\t(symbol")
        lines.append(f'\t  (lib_id "{sym.lib_id}")')
        lines.append(f"\t  (at {sym.position[0]:.2f} {sym.position[1]:.2f} {sym.rotation:.1f})")
        lines.append(f"\t  (unit {sym.unit})")
        lines.append("\t  (exclude_from_sim no)")
        lines.append(f"\t  (in_bom {'yes' if sym.in_bom else 'no'})")
        lines.append(f"\t  (on_board {'yes' if sym.on_board else 'no'})")
        lines.append("\t  (dnp no)")
        lines.append("\t  (fields_autoplaced yes)")
        lines.append(f"\t  (uuid \"{sym.uuid}\")")
        lines.append(f'\t  (property "Reference" "{sym.reference}"')
        lines.append(f"\t    (at {sym.position[0]+2.0:.2f} {sym.position[1]:.2f} 0)")
        lines.append("\t    (effects (font (size 1.27 1.27)))")
        lines.append("\t  )")
        lines.append(f'\t  (property "Value" "{sym.value}"')
        lines.append(f"\t    (at {sym.position[0]+2.0:.2f} {sym.position[1]+1.5:.2f} 0)")
        lines.append("\t    (effects (font (size 1.27 1.27))))")
        lines.append(f'\t  (property "Footprint" "{sym.footprint}"')
        lines.append(f"\t    (at {sym.position[0]:.2f} {sym.position[1]:.2f} 0)")
        lines.append("\t    (effects (font (size 1.27 1.27)) (hide yes))")
        lines.append("\t  )")
        lines.append("\t)")
        return "\n".join(lines)

    def generate(self, out_file: str) -> bool:
        try:
            lines = []
            lines.append("(kicad_sch")
            lines.append(f"\t(version {self.version})")
            lines.append(f"\t(generator \"{self.generator}\")")
            lines.append(f"\t(generator_version \"{self.generator_version}\")")
            lines.append(f"\t(uuid \"{self.uuid}\")")
            lines.append(f"\t(paper \"{self.paper_size}\")")

            # Minimal title block
            dt_str = datetime.datetime.now().strftime("%Y-%m-%d")
            lines.append("\t(title_block")
            lines.append(f"\t\t(date \"{dt_str}\")")
            lines.append("\t)")

            # Flattened library symbols
            lines.append(self._generate_lib_symbols_section())

            # Symbol instances
            for s in self.symbols:
                lines.append(self._generate_symbol_instance(s))

            # minimal sheet_instances
            lines.append("\t(sheet_instances")
            lines.append("\t\t(path \"/\" (page \"1\"))")
            lines.append("\t)")
            lines.append(")")

            text = "\n".join(lines) + "\n"
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(text)

            return True
        except Exception as e:
            print(f"[Error writing schematic {out_file}]: {e}")
            return False
