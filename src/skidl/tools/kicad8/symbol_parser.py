#!/usr/bin/env python3
"""
symbol_parser.py

Parses KiCad .kicad_sym files into structured SymbolDefinition objects,
handling inheritance `(extends "Parent")` by merging parent + child data.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

@dataclass
class Pin:
    """
    Minimal representation of a pin within a symbol.
    Extend as needed: shape, electrical type, etc.
    """
    number: str
    name: Optional[str] = None


@dataclass
class SymbolDefinition:
    """
    A single symbol's structured data. Once flattened, 'extends' is None,
    and it has the parent's pins/properties merged in.
    """
    name: str
    extends: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    pins: List[Pin] = field(default_factory=list)
    raw_shapes: List[str] = field(default_factory=list)

    is_flattened: bool = False  # Track if we've done the merge


class SymbolParser:
    """
    Loads an entire .kicad_sym file, capturing each `(symbol ...)` block.
    Parses them into SymbolDefinition objects.

    Then, get_flattened_symbol(sym_name) merges any parent data so that
    the final result has no `(extends ...)` (i.e., is fully inherited).
    """

    def __init__(self, libfile: str):
        self.libfile = libfile
        self.loaded = False
        self.symbols: Dict[str, SymbolDefinition] = {}  # symbol_name -> SymbolDefinition

    def load_library(self) -> None:
        """
        Parse the entire library file if not already loaded, populating self.symbols.
        """
        if self.loaded:
            return

        if not os.path.isfile(self.libfile):
            raise FileNotFoundError(f"Library file not found: {self.libfile}")

        with open(self.libfile, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        i = 0
        n = len(all_lines)

        # A simple bracket-based approach: find each top-level "(symbol ... )"
        while i < n:
            line = all_lines[i].strip()
            if line.startswith("(symbol "):
                symbol_lines, next_i = self._collect_block(all_lines, i)
                i = next_i
                sdef = self._parse_symbol_block(symbol_lines)
                self.symbols[sdef.name] = sdef
            else:
                i += 1

        self.loaded = True

    def _collect_block(self, lines: List[str], start_idx: int):
        """
        Return all lines from the initial '(symbol' to its matching closing ')'.
        i.e. bracket matching.
        """
        block_lines = []
        bracket_count = 0
        i = start_idx
        n = len(lines)
        while i < n:
            l = lines[i]
            block_lines.append(l)
            # update bracket count
            bracket_count += l.count("(")
            bracket_count -= l.count(")")
            i += 1
            if bracket_count <= 0:
                break
        return block_lines, i

    def _parse_symbol_block(self, sym_lines: List[str]) -> SymbolDefinition:
        """
        Convert lines from a single `(symbol "Foo" (extends "Bar") ...)` block
        into a SymbolDefinition. The parse is naive, but workable for demonstration.
        """
        raw_text = "\n".join(sym_lines)
        # The first line typically includes (symbol "Child" (extends "Parent") ...
        # We attempt to detect that.

        # Example first line:
        # (symbol "NCP1117-3.3_SOT223" (extends "AP1117-15")
        first_line = sym_lines[0].strip()
        name = None
        extends_name = None

        idx = first_line.find("(symbol ")
        if idx >= 0:
            rest = first_line[idx+8:].strip()  # e.g. '"NCP1117..." (extends "...") ...'
            if rest.startswith('"'):
                second_quote = rest.find('"', 1)
                name = rest[1:second_quote]
                after_name = rest[second_quote+1:].strip()
                # detect extends
                if "(extends " in after_name:
                    eq = after_name.find("(extends")
                    # eq2 is where the extends param starts
                    ext_sub = after_name[eq:]
                    # e.g. '(extends "AP1117-15")'
                    q1 = ext_sub.find('"')
                    q2 = ext_sub.find('"', q1+1)
                    extends_name = ext_sub[q1+1:q2]

        if not name:
            name = "UnknownSymbol"

        sdef = SymbolDefinition(name=name, extends=extends_name)

        # Next, parse line by line for (property ...), (pin ...), shapes, etc.
        # Real code would do a real s-expression parse, but let's keep it short.
        for ln in sym_lines:
            ln_str = ln.strip()

            # skip top-level extends expression
            if "(extends " in ln_str:
                continue

            if ln_str.startswith("(property "):
                # e.g. (property "Value" "10uF" (at 2.54 3.81) ...)
                parts = ln_str.split('"')
                if len(parts) >= 4:
                    prop_name = parts[1]
                    prop_val = parts[3]
                    sdef.properties[prop_name] = prop_val

            elif ln_str.startswith("(pin "):
                # naive parse: the first quoted substring is the pin number
                # e.g. (pin "1" (uuid ...) (alternate "A") ...)
                # or (pin "3")
                pparts = ln_str.split('"')
                if len(pparts) >= 2:
                    pin_number = pparts[1]
                    sdef.pins.append(Pin(number=pin_number))
                # in a real parse, you'd detect shape/electrical type, etc.

            elif ln_str.startswith("(symbol "):
                # skip nested unit definitions or sub-symbol blocks
                pass
            else:
                # Possibly a shape line. We store it to re-inject later.
                sdef.raw_shapes.append(ln_str)

        return sdef

    def get_flattened_symbol(self, sym_name: str) -> Optional[SymbolDefinition]:
        """
        Return a fully flattened (no extends) SymbolDefinition for `sym_name`.
        """
        self.load_library()
        if sym_name not in self.symbols:
            return None
        return self._flatten_symbol(sym_name, visited=set())

    def _flatten_symbol(self, sym_name: str, visited: Set[str]) -> SymbolDefinition:
        """
        Recursively merges child->parent. The child's data overrides parent's.
        """
        if sym_name in visited:
            raise ValueError(f"Cycle in extends for {sym_name}")
        visited.add(sym_name)

        sym_def = self.symbols[sym_name]
        if sym_def.is_flattened:
            return sym_def

        if sym_def.extends:
            parent_def = self._flatten_symbol(sym_def.extends, visited)
            self._merge_symbol_defs(parent_def, sym_def)

        sym_def.is_flattened = True
        return sym_def

    def _merge_symbol_defs(self, parent: SymbolDefinition, child: SymbolDefinition):
        """
        Combine parent's data into child. Child overrides any matching property/pin.
        Then remove child's extends reference so it no longer references the parent.
        """
        # Merge properties
        for k, v in parent.properties.items():
            if k not in child.properties:
                child.properties[k] = v

        # Merge pins (naive approach: child overrides only if same pin number)
        child_pin_nums = {p.number for p in child.pins}
        for pp in parent.pins:
            if pp.number not in child_pin_nums:
                child.pins.append(pp)

        # Merge shapes: if child wants to override, you'd do something more advanced.
        # We'll just append parent's shapes first, then child's.
        old_child_shapes = child.raw_shapes
        child.raw_shapes = parent.raw_shapes + old_child_shapes

        # Clear child's extends
        child.extends = None

