# SKiDL Converter Architecture

## Core Components

### SheetToSkidlConverter (sheet_to_skidl.py)
- Entry point for conversion process
- Coordinates parsing hierarchy and generating SKiDL code
- Implements visitor pattern for schematic traversal

### Component Handling
- `ComponentParser` class (component_parser.py)
  - Extracts manufacturer part numbers
  - Handles symbol-to-footprint mapping
  - Integrates with KiCad libraries

### Hierarchy Processing
- Recursive sheet parsing
- Power port inheritance
- Net alias propagation across hierarchy levels

## Key Architectural Decisions

1. **Modular Parser Design**
   - Separation of concerns between schematic elements
   - Each parser class handles specific element type (wires, labels, components)

2. **Visitor Pattern Implementation**
   - Enables clean extension for new element types
   - Maintains single responsibility principle

3. **Coordinate Transformation**
   - Converts KiCad's Y-up coordinate system to SKiDL's standard layout
   - Matrix transformation preserves spatial relationships

## Test Coverage

```python
# test_resistor_divider.py
def test_resistor_network():
    # Validates:
    # - Correct net connections
    # - Voltage divider ratio
    # - Power net inheritance
    pass
```

## Suggested Improvements
- [ ] Hierarchical net labeling support
- [ ] Automated BOM generation integration
- [ ] 3D layout visualization hooks
