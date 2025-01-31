"""
kicad_library_parser.py

Responsible for parsing a .kicad_sym file into structured SymbolDefinition objects
including the (extends ...) relationship.
"""

import os
from typing import Dict, Set, List, Optional
from .symbol_definitions import SymbolDefinition, ShapeDefinition, PinDefinition

class KicadLibraryParser:
    def __init__(self, libfile: str):
        self.libfile = libfile
        self.symbols: Dict[str, SymbolDefinition] = {}
        self._loaded = False

    def load_library(self) -> None:
        """Read the .kicad_sym file, parse out each (symbol "Name" (extends "...") ...) block."""
        if self._loaded:
            return

        if not os.path.isfile(self.libfile):
            raise FileNotFoundError(f"KiCad library file not found: {self.libfile}")

        with open(self.libfile, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # We'll do a simplistic bracket matcher to gather lines for each symbol
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i].strip()
            # Look for top-level (symbol "SomeName" ...
            if line.startswith("(symbol "):
                bracket_count = line.count("(") - line.count(")")
                sym_lines = [line]
                i += 1
                while i < n and bracket_count > 0:
                    ln2 = lines[i]
                    sym_lines.append(ln2.rstrip("\n"))
                    bracket_count += ln2.count("(")
                    bracket_count -= ln2.count(")")
                    i += 1

                # parse the first line for name & extends
                sym_def = self._parse_symbol_block(sym_lines)
                if sym_def:
                    self.symbols[sym_def.name] = sym_def
            else:
                i += 1

        self._loaded = True

    def _parse_symbol_block(self, sym_lines: List[str]) -> Optional[SymbolDefinition]:
        """
        Parse the lines for a single (symbol "Name" (extends "Parent") ...).
        We'll do a naive string search for name=..., extends=..., but do not fully parse shapes.
        """
        if not sym_lines:
            return None
        first_line = sym_lines[0].strip()
        # e.g. (symbol "NCP1117-3.3_SOT223" (extends "AP1117-15")
        # We'll parse out the name
        name = None
        extends_parent = None

        # Simple approach: find (symbol "Name"
        # We can do robust searching or a quick substring approach
        if first_line.startswith("(symbol "):
            # skip (symbol
            after_symbol = first_line[len("(symbol "):].strip()
            if after_symbol.startswith('"'):
                # find second quote
                second_quote = after_symbol.find('"', 1)
                if second_quote > 1:
                    name = after_symbol[1:second_quote]
                    rest = after_symbol[second_quote+1:].strip()
                    # if we see (extends "something")
                    if "(extends" in rest:
                        # e.g. (extends "AP1117-15")
                        # find the first quote after (extends
                        ext_idx = rest.find('(extends')
                        first_q = rest.find('"', ext_idx)
                        second_q = rest.find('"', first_q+1)
                        if first_q > 0 and second_q > first_q:
                            extends_parent = rest[first_q+1:second_q]
            else:
                # fallback
                # might have e.g. (symbol MySymbol (extends Another)
                pass

        if not name:
            # fallback name
            return None

        sym_def = SymbolDefinition(name=name, extends=extends_parent)

        # Next steps: find sub-things like (property ...), (pin ...), etc.
        # We'll do a partial parse to demonstrate how to store pins, properties, shapes
        # For a real parser, you'd tokenize everything. We'll do a partial approach:
        joined = "\n".join(sym_lines)

        # A naive property parse:
        # For example lines like: (property "Reference" "U"
        # We skip that for brevity or do a minimal parse:

        # For a real solution, you'd do a real s-expression parse. We'll just store the raw lines
        # for shapes, then do a real flatten approach that merges them. We'll store them in
        # sym_def.shapes for demonstration, or skip.

        return sym_def

    def get_symbols(self) -> Dict[str, SymbolDefinition]:
        self.load_library()
        return self.symbols
