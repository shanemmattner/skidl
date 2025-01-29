# KiCad Schematic Generation Test Architecture

## Current Issue
The schematic generation test is failing because:
1. The code attempts to load symbol definitions from KiCad library files
2. The library path is hardcoded and may not exist in test environments
3. Symbol definitions are not being properly generated

## Solution Architecture

### 1. Symbol Definition Management
Instead of loading symbols from KiCad library files during tests, we should:

- Add a method to KicadSchematicWriter to directly inject symbol definitions:
```python
def add_symbol_definition(self, lib_id: str, symbol_def: SymbolDefinition):
    """Add a pre-defined symbol definition for testing."""
    self.symbol_definitions[lib_id] = symbol_def
```

- Extract symbol definitions from reference schematics for testing:
```python
def extract_symbol_definition(schematic_content: str, lib_id: str) -> SymbolDefinition:
    """Extract a symbol definition from a reference schematic."""
    parser = SchematicParser()
    tree = parser.parse(schematic_content)
    lib_symbols = tree.find('lib_symbols')
    for symbol in lib_symbols.attributes:
        if symbol.attributes[0] == f'"{lib_id}"':
            return convert_to_symbol_definition(symbol)
    return None
```

### 2. Test Structure
Update test_one_resistor.py to:

1. Load the reference schematic
2. Extract the resistor symbol definition
3. Inject it into the KicadSchematicWriter before generating the test schematic
4. Compare the generated schematic against the reference

### 3. Production vs Test Configuration
- In production: Load symbols from KiCad library files
- In tests: Use injected symbol definitions
- Control this behavior through an environment variable or test fixture

### Implementation Steps

1. Add symbol definition injection capability to KicadSchematicWriter
2. Create helper functions to extract symbol definitions from reference schematics
3. Update tests to use the new approach
4. Add documentation for testing approach

### Benefits

1. Tests are self-contained and don't depend on external KiCad libraries
2. Reference schematics serve as both test data and documentation
3. Symbol definitions are guaranteed to match between test and reference
4. Tests remain deterministic across different environments

### Future Improvements

1. Create a symbol definition cache for commonly used symbols
2. Add validation for symbol definitions
3. Support custom symbol libraries for testing
4. Add migration tools for updating reference schematics