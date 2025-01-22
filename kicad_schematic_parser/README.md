# SKiDL KiCad Schematic Parser

A Python module for SKiDL that parses and analyzes KiCad schematic files, converting them to SKiDL Python code. This module operates in two stages:
1. KiCad Schematic to Text: Extracts comprehensive information about components, pins, connections, and labels from KiCad schematics
2. Text to SKiDL: Converts the extracted information into SKiDL Python code for circuit definition

## Current Status

### KiCad to Text (Complete)
- ✅ Component extraction with detailed properties
- ✅ Pin position calculation with support for rotated components
- ✅ Wire connection analysis
- ✅ Label parsing (local, hierarchical, and power labels)
- ✅ Net connectivity analysis
- ✅ Support for hierarchical sheets

### Text to SKiDL (In Progress)
- ✅ Component parsing
- 🚧 Pin and connection parsing (Planned)
- 🚧 Net parsing (Planned)
- 🚧 Sheet structure parsing (Planned)
- 🚧 Circuit hierarchy building (Planned)
- 🚧 SKiDL code generation (Planned)

## Usage

The tool supports two modes of operation:

### 1. KiCad to Text Conversion
```bash
python src/main.py --mode kicad2text <schematic_file_path>
```

This will analyze the schematic and output a text file containing:
- Component list with properties
- Pin details including positions and types
- Wire connections
- Label information (local, hierarchical, power)
- Complete netlist showing connectivity

### 2. Text to SKiDL Conversion (Coming Soon)
```bash
python src/main.py --mode text2skidl <text_file_path>
```

This will convert the text representation into SKiDL Python code.

## Project Structure

```
src/
├── main.py                     # Main entry point with dual mode support
├── kicad_hierarchy_parser/     # KiCad to Text conversion
│   ├── parser.py              # Main parser functionality
│   ├── components/            # Component parsing
│   │   └── component_parser.py
│   ├── connectivity/          # Wire and net analysis
│   │   ├── wire_parser.py
│   │   └── net_parser.py
│   ├── labels/                # Label parsing
│   │   └── label_parser.py
│   └── utils/                 # Utility functions
│       └── geometry.py
└── skidl_generator/           # Text to SKiDL conversion
    ├── component_parser/      # Phase 1: Parse component information
    ├── pin_parser/           # Phase 2: Parse pin information
    ├── net_parser/           # Phase 3: Parse net information
    ├── sheet_parser/         # Phase 4: Parse sheet structure
    ├── hierarchy_builder/    # Phase 5: Build circuit hierarchy
    └── code_generator/       # Phase 6: Generate SKiDL code
```

## Known Bugs

### KiCad to Text
- Labels placed in the middle of a wire do not always get detected
- Labels might not transfer when connected
  - ie 5v connected to label1, then label1 connected to label2. label2 might not be connected to 5v

## Development

The project is organized into two main modules:

### KiCad Hierarchy Parser
- Handles KiCad schematic file parsing
- Extracts component and pin information
- Analyzes wire connections and nets
- Processes different types of schematic labels

### SKiDL Generator
- Converts text representation to SKiDL code
- Follows modular approach with separate parsers
- Handles component properties and connections
- Manages circuit hierarchy and sheet structure

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

Pin Placement Tests:
- Component pin position calculations
- Support for rotated components
- Pin electrical type verification
- Tests using power supplies, resistor dividers, and microcontroller schematics

Wire Connection Tests:
- Wire connectivity analysis
- Net detection and verification
- Power and ground connections
- Local and hierarchical label connections
- Tests using voltage monitoring and power supply circuits

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
