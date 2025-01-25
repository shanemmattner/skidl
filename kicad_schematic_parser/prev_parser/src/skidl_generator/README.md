# SKiDL Generator

## Overview
Converts KiCad hierarchy text files into executable SKiDL Python code. Implements schematic-to-netlist conversion with:
- Component parsing and validation
- Net connectivity analysis
- Hierarchical port handling
- Power net detection
- Deterministic code generation

## Key Features
```python
from skidl_generator.sheet_to_skidl import sheet_to_skidl

# Convert schematic text to SKiDL 
with open('resistor_divider.txt') as f:
    skidl_code = sheet_to_skidl("VoltageDivider", f.read())

# Generated code includes:
# - Component declarations
# - Net connections 
# - Hierarchical I/O ports
# - Power net handling (GND)
```

## Test Suite
Validates conversion logic through comprehensive tests:
```bash
# Run all SKiDL conversion tests
pytest src/skidl_generator/tests/sheet_to_skidl/ -v
```

## Implementation Details
- **Data Structures**: `Component` and `Net` dataclasses enforce type safety
- **Section Parsing**: Handles Components/Netlist/Power sections
- **Code Generation**: Produces human-readable SKiDL with proper pin ordering
- **Validation**: 100% test coverage on core conversion logic

## Suggested Improvements
See [SUGGESTED_IMPROVEMENTS.md](src/skidl_generator/sheet_to_skidl/SUGGESTED_IMPROVEMENTS.md) for:
- Enhanced error handling
- Multi-unit component support
- Bus connection handling
- Extended test coverage
