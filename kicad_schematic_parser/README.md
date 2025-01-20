# KiCad Schematic Parser

A Python tool for parsing and analyzing KiCad schematic files. This tool extracts comprehensive information about components, pins, connections, and labels from KiCad schematics.

## Features

- Component extraction with detailed properties
- Pin position calculation with support for rotated components
- Wire connection analysis
- Label parsing (local, hierarchical, and power labels)
- Net connectivity analysis
- Support for hierarchical sheets

## Project Structure

```
src/
├── main.py                     # Main entry point
└── kicad_parser/              # Main package
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

Tests are included in the `tests` directory and can be run using pytest.

## Dependencies

- Python 3.6+
- kiutils (for KiCad schematic file parsing)

## License

[Add your license information here]
