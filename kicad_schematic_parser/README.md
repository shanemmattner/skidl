# SKiDL KiCad Schematic Parser

A Python module for SKiDL that parses and analyzes KiCad schematic files. This module enables SKiDL to extract comprehensive information about components, pins, connections, and labels from KiCad schematics, allowing for circuit definition in code.

## Features

- Component extraction with detailed properties
- Pin position calculation with support for rotated components
- Wire connection analysis
- Label parsing (local, hierarchical, and power labels)
- Net connectivity analysis
- Support for hierarchical sheets

## Known Bugs
- Lables placed in the middle of a wire do not always get detected
- Labels might not transfer when connected
  - ie 5v connected to label1, then label1 connected to label2.  label2 might not be connected to 5v

## Project Structure

```
src/
├── main.py                     # Main entry point
└── skidl_kicad_parser/        # Main package for SKiDL integration
    ├── __init__.py            # Package initialization
    ├── parser.py              # Main parser functionality
    ├── components/            # Component parsing
    │   └── component_parser.py
    ├── connectivity/          # Wire and net analysis
    │   ├── wire_parser.py
    │   └── net_parser.py
    ├── labels/                # Label parsing
    │   └── label_parser.py
    ├── utils/                 # Utility functions
    │   └── geometry.py
    └── tests/                 # Test files
        ├── conftest.py
        ├── test_pin_positions.py
        └── test_schematics/   # Test schematic files
```

## Usage

```bash
python src/main.py <schematic_file_path>
```

The tool will analyze the schematic and output:
- Component list with properties
- Pin details including positions and types
- Wire connections
- Label information (local, hierarchical, power)
- Complete netlist showing connectivity

## Example Output

```
=== Components ===
Component: Device/C
Properties:
  Reference: C11
  Value: C
  Footprint: Capacitor_SMD:C_0603_1608Metric
...

=== Pin Details ===
Component: C11
  Pin 1 (~):
    Position: (133.35, 68.58)
    Type: passive
...

=== Labels ===
Local Labels:
  label_test_power3 at (193.04, 99.06)
...

=== Netlist ===
+3V3:
  Pins:
    C11 Pin 1 (~)
    U4 Pin 2 (VO)
  Power Labels:
    +3V3
...
```

## Development

The project is organized into modules:
- `components`: Handles component and pin parsing
- `connectivity`: Manages wire connections and net analysis
- `labels`: Processes different types of schematic labels
- `utils`: Contains common utility functions

### Running Tests

Tests are located in `src/kicad_parser/tests`. To run the tests:

1. Install pytest if you haven't already:
```bash
pip install pytest
```

2. Run tests from the project root:
```bash
pytest
```

The test suite includes:
- Pin position calculations
- Component parsing
- Wire connectivity analysis
- Label detection
- Net analysis

Test schematics are included in `src/kicad_parser/tests/test_schematics/`.

## Dependencies

- Python 3.6+
- SKiDL (for circuit definition in code)
- kiutils (for KiCad schematic file parsing)

## Integration with SKiDL

This module is designed to be integrated with SKiDL, a Python package that allows you to define electronic circuits using Python code. The parser extracts KiCad schematic information that can be used to:

1. Create SKiDL Circuit objects from existing KiCad schematics
2. Convert between SKiDL and KiCad representations
3. Enable hybrid workflows combining code-defined and schematic-captured circuits

For more information about SKiDL, visit: [SKiDL Documentation](https://xesscorp.github.io/skidl/docs/_site/)

## License

[Add your license information here]
