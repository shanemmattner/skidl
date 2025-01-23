# SKiDL Generator

## Overview
This module is responsible for converting KiCad hierarchy text files into SKiDL Python code. It follows a modular approach with separate parsers for different aspects of the circuit.

## Directory Structure

```
skidl_generator/
├── component_parser/    # Phase 1: Parse component information
├── pin_parser/         # Phase 2: Parse pin and connection information
├── net_parser/         # Phase 3: Parse net information
├── sheet_parser/       # Phase 4: Parse sheet structure
├── hierarchy_builder/  # Phase 5: Build circuit hierarchy
└── code_generator/     # Phase 6: Generate SKiDL Python code
```

## Testing

### Test Structure
Tests are organized into separate packages for each parsing module:
```
tests/
├── component_tests/
├── hierarchy_tests/
├── net_tests/
├── pin_tests/
└── conftest.py
```

### Running Tests
To run tests, use pytest:
```bash
pytest src/skidl_generator/tests
```

### Adding New Tests
1. Create tests in the appropriate subdirectory
2. Follow existing test patterns
3. Use placeholder tests as a template for new modules

## Module Descriptions

### Component Parser
- Parses component information from hierarchy text files
- Extracts component properties (reference, value, footprint, etc.)
- Validates component data format

### Pin Parser (Future)
- Will handle pin definitions and connections
- Will track pin electrical types and positions
- Will manage pin-to-pin connections

### Net Parser (Future)
- Will parse net names and connections
- Will handle power nets, local nets, and hierarchical nets
- Will track net connectivity

### Sheet Parser (Future)
- Will parse sheet definitions and boundaries
- Will handle sheet properties and metadata
- Will track parent-child relationships

### Hierarchy Builder (Future)
- Will construct the complete circuit hierarchy
- Will manage sheet relationships
- Will resolve cross-sheet connections

### Code Generator (Future)
- Will generate SKiDL Python code
- Will create subcircuit functions
- Will handle component instantiation and connections

## Development Status
- Component Parser: Complete
- Other modules: Planned for future development

## Usage
Currently, only the component parser is implemented. Example usage:

```python
from skidl_generator.component_parser import parse_component_name, parse_component_properties

# Parse a component name
result = parse_component_name("Component: Device/R")
if result.success:
    library, component = result.data

# Parse component properties
lines = [
    "Properties:",
    "    Reference: R1",
    "    Value: 10K"
]
result = parse_component_properties(lines)
if result.success:
    component = result.data
```

## Future Development
Follow the development plan in docs_utils/skidl_parser_development_plan.md for implementing additional modules.
