# KiCad Symbol Generation Fix

## Issue
The resistor symbols are not being properly generated in the schematic because:
1. The lib_symbols section is missing from the generated schematic
2. Symbol definitions are not being properly translated from lib.py
3. Symbol instances are not correctly referencing the defined symbols

## Required Changes

### 1. KicadSchematicWriter Changes

The generate() method needs to be updated to:
1. Include a lib_symbols section
2. Collect all unique symbols used in the schematic
3. Generate proper symbol definitions including:
   - Properties (Reference, Value, Footprint, etc.)
   - Pin definitions
   - Shape definitions (rectangles, lines, etc.)

```python
def generate(self):
    """
    Generate the .kicad_sch file:
    1) Write schematic header
    2) Write lib_symbols section with all used symbols
    3) Write symbol instances
    4) Write sheet instances
    """
```

### 2. Symbol Definition Structure

The lib_symbols section should contain:

```scheme
(lib_symbols
    (symbol "Device:R"
        (pin_numbers hide)
        (pin_names (offset 0))
        (exclude_from_sim no)
        (in_bom yes)
        (on_board yes)
        (properties...)
        (symbol shapes...)
        (pins...)
    )
)
```

### 3. Symbol Properties

Required properties for resistor symbol:
- Reference: "R" at (2.032 0 90)
- Value: "R" at (0 0 90)
- Footprint: "" at (-1.778 0 90)
- Datasheet: "~"
- Description: "Resistor"
- ki_keywords: "R res resistor"
- ki_fp_filters: "R_*"

### 4. Symbol Shapes

Two shape definitions needed:
1. R_0_1: Basic rectangle shape
2. R_1_1: Pin definitions

### 5. Integration with lib.py

Use lib.py's Part object to:
1. Get symbol properties
2. Get pin definitions
3. Get shape definitions

### Implementation Steps

1. Update KicadSchematicWriter:
```python
def _collect_symbols(self):
    """Collect all unique symbols used in instances"""
    symbols = {}
    for inst in self.symbol_instances:
        lib_id = inst.lib_id
        if lib_id not in symbols:
            symbols[lib_id] = inst.part
    return symbols

def _write_lib_symbols(self, lines):
    """Write lib_symbols section with all used symbols"""
    lines.append("  (lib_symbols")
    symbols = self._collect_symbols()
    for lib_id, part in symbols.items():
        self._write_symbol_definition(lines, lib_id, part)
    lines.append("  )")
```

2. Add symbol definition writer:
```python
def _write_symbol_definition(self, lines, lib_id, part):
    """Write complete symbol definition including properties and shapes"""
    lines.append(f'    (symbol "{lib_id}"')
    self._write_symbol_properties(lines, part)
    self._write_symbol_shapes(lines, part)
    self._write_symbol_pins(lines, part)
    lines.append("    )")
```

### Testing

1. Generate a simple resistor schematic
2. Compare output with reference schematic
3. Verify all symbol properties are correct
4. Check pin and shape definitions
5. Validate symbol instances reference the symbols correctly

## Benefits

1. More accurate symbol generation
2. Better integration with lib.py
3. Proper symbol inheritance support
4. Consistent with KiCad's schematic format

## Future Improvements

1. Cache symbol definitions for reuse
2. Support more symbol types
3. Add symbol validation
4. Improve error handling for missing symbols