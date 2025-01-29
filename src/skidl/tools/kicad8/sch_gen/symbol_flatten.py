"""
symbol_flatten.py

Implements the multi-level inheritance flattening:
Child inherits from parent. If child.extends is set,
recursively flatten the parent, then merge.
"""

from typing import Dict, Set
from .symbol_definitions import SymbolDefinition

class SymbolFlattener:
    def __init__(self, symbols: Dict[str, SymbolDefinition]):
        """
        'symbols' is the dictionary of name -> SymbolDefinition from the parser.
        """
        self.symbols = symbols
        self.flattened_cache: Dict[str, SymbolDefinition] = {}

    def get_flattened_symbol(self, sym_name: str) -> SymbolDefinition:
        """Return a *copy* of the fully flattened symbol definition for 'sym_name'."""
        if sym_name in self.flattened_cache:
            return self.flattened_cache[sym_name]

        if sym_name not in self.symbols:
            raise ValueError(f"Symbol {sym_name} not found in dictionary")

        # We will do a deep copy to avoid modifying the original
        from copy import deepcopy
        original_sym = self.symbols[sym_name]
        copy_sym = deepcopy(original_sym)

        visited: Set[str] = set()
        self._flatten_recursive(copy_sym, visited)

        # Now store it in the cache
        self.flattened_cache[sym_name] = copy_sym
        return copy_sym

    def _flatten_recursive(self, child: SymbolDefinition, visited: Set[str]) -> None:
        if child.name in visited:
            raise ValueError(f"Cyclical extends found on symbol: {child.name}")
        visited.add(child.name)

        if not child.extends:
            return  # no parent => already root

        parent_name = child.extends
        if parent_name not in self.symbols:
            raise ValueError(f"Parent symbol {parent_name} not found in dictionary")

        parent_def = self.symbols[parent_name]
        # Recursively flatten the parent
        if parent_name in self.flattened_cache:
            parent_flat = self.flattened_cache[parent_name]
        else:
            # might need a fresh deep copy
            from copy import deepcopy
            parent_copy = deepcopy(parent_def)
            self._flatten_recursive(parent_copy, visited)
            # store result
            self.flattened_cache[parent_name] = parent_copy
            parent_flat = parent_copy

        # MERGE parent_flat -> child
        self._merge_symbols(child, parent_flat)

        # remove extends
        child.extends = None

    def _merge_symbols(self, child: SymbolDefinition, parent: SymbolDefinition) -> None:
        """
        Merge parent's content into child's. Child overrides if there's a conflict.
        E.g. parent's property "Datasheet" is used only if child has no "Datasheet".
        For pins, if child redefines the same pin number, child's version wins.
        For shapes, we can just append them for simplicity, or do advanced override logic.
        """
        # 1) Merge properties
        for k, v in parent.properties.items():
            if k not in child.properties:
                child.properties[k] = v

        # 2) Merge pins
        for pin_num, parent_pin in parent.pins.items():
            if pin_num not in child.pins:
                child.pins[pin_num] = parent_pin

        # 3) Merge shapes (for demonstration, just append parent's shapes)
        for shape in parent.shapes:
            child.shapes.append(shape)
