# KiCad Symbol Library Integration

## Current Issues
1. Naive string-based parsing of .kicad_sym files
2. Incomplete symbol definition parsing
3. Symbol inheritance not fully resolved
4. Hard-coded library paths and symbol references

## Proposed Solution

### 1. KiCad Symbol File Parsing
```python
class KiCadSymbolParser:
    """
    Properly parse KiCad .kicad_sym files using s-expression parsing:
    - Use proper s-expression tokenization
    - Handle nested structures correctly
    - Parse all symbol elements (properties, pins, shapes)
    - Support symbol inheritance
    """
    def parse_symbol_file(self, filepath: str) -> Dict[str, SymbolDefinition]:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Use proper s-expression parsing
        tokens = tokenize_sexpr(content)
        symbols = {}
        
        for expr in parse_sexpr(tokens):
            if expr[0] == 'symbol':
                symbol = self._parse_symbol_expr(expr)
                symbols[symbol.name] = symbol
                
        return symbols
        
    def _parse_symbol_expr(self, expr) -> SymbolDefinition:
        """Parse complete symbol definition including:
        - Name and inheritance
        - Properties (Reference, Value, etc)
        - Pins with full attributes
        - Shapes and graphics
        - Units and conversions
        """
        # Implementation details...
```

### 2. KiCad Library Resolution
```python
class KiCadLibraryResolver:
    """
    Find and load KiCad symbol libraries:
    - Use KiCad's library table files
    - Support global and project libraries
    - Handle library priorities
    """
    def get_library_table_paths(self) -> List[str]:
        """Get paths to sym-lib-table files:
        1. Global ($HOME/.config/kicad/VERSION/sym-lib-table)
        2. Project (project_dir/sym-lib-table)
        """
        paths = []
        # Implementation details...
        return paths
        
    def resolve_library(self, lib_id: str) -> Tuple[str, str]:
        """
        Convert library:symbol ID to actual file path:
        - Parse library tables
        - Handle environment variables
        - Support library aliases
        """
        lib_name, symbol_name = lib_id.split(':')
        return self._find_library_file(lib_name), symbol_name
```

### 3. Symbol Resolution
```python
class SymbolResolver:
    """
    Resolve complete symbol definitions:
    - Handle symbol inheritance
    - Merge parent/child attributes
    - Validate final symbol
    """
    def resolve_symbol(self, lib_id: str) -> SymbolDefinition:
        """
        Get complete symbol definition:
        1. Find library file
        2. Parse symbol
        3. Resolve inheritance
        4. Validate result
        """
        lib_file, sym_name = self.lib_resolver.resolve_library(lib_id)
        symbols = self.parser.parse_symbol_file(lib_file)
        
        if sym_name not in symbols:
            raise SymbolNotFoundError(f"Symbol {sym_name} not found in {lib_file}")
            
        return self._resolve_inheritance(symbols[sym_name], lib_file)
        
    def _resolve_inheritance(self, symbol: SymbolDefinition, lib_file: str) -> SymbolDefinition:
        """
        Handle symbol inheritance:
        - Load parent symbols
        - Apply inheritance rules
        - Merge attributes
        """
        if not symbol.extends:
            return symbol
            
        parent = self._load_parent_symbol(symbol.extends, lib_file)
        return self._merge_symbols(parent, symbol)
```

## Implementation Guidelines

1. **Library Resolution**
   - Use KiCad's library table files (sym-lib-table)
   - Support environment variables (KICAD7_SYMBOL_DIR, etc)
   - Handle library priorities correctly

2. **Symbol Parsing**
   - Use proper s-expression parsing
   - Parse all symbol elements completely
   - Maintain original symbol structure

3. **Inheritance Handling**
   - Load complete parent symbols
   - Apply KiCad's inheritance rules
   - Validate merged symbols

4. **Error Handling**
   - Provide clear error messages
   - Include context (file, line number)
   - Support validation warnings

## Benefits

1. **Reliability**
   - Uses KiCad's actual symbol definitions
   - Handles all symbol features
   - Proper inheritance support

2. **Maintainability**
   - No hard-coded paths
   - Uses KiCad's configuration
   - Clear separation of concerns

3. **Compatibility**
   - Works with any KiCad symbol
   - Supports custom libraries
   - Future-proof design

## Next Steps

1. Implement proper s-expression parser
2. Add KiCad library table support
3. Complete symbol inheritance resolution
4. Add comprehensive validation