# KiCad Component Parser

## Overview

This module is part of the SKiDL Parser project, designed to parse component information from KiCad hierarchical netlists. The component parser focuses on extracting and validating component details such as library, name, reference, value, and other properties.

## Functionality

The component parser provides two primary parsing functions:

1. **Component Name Parsing** (`parse_component_name()`)
   - Extracts library and component name from a line
   - Validates the format (must be `library/component`)
   - Returns a `ParseResult` with library and component name

2. **Component Properties Parsing** (`parse_component_properties()`)
   - Parses a list of component properties
   - Extracts details like:
     - Reference
     - Value
     - Footprint
     - Datasheet
     - Description
     - UUID
   - Returns a `ParseResult` with a `Component` object

## Error Handling

The parser uses a robust error handling mechanism:

- `ParseResult` class tracks parsing success and errors
- `ParseError` captures line number, content, and error message
- Detailed validation prevents silent failures

## Example Usage

```python
# Parsing component name
result = parse_component_name("Component: Device/R")
if result.success:
    library, component = result.data
else:
    for error in result.errors:
        print(f"Error on line {error.line_num}: {error.message}")

# Parsing component properties
lines = [
    "Properties:",
    "    Reference: R1",
    "    Value: 10K",
    "    Footprint: Resistor_SMD:R_0603_1608Metric"
]
result = parse_component_properties(lines)
if result.success:
    component = result.data
    print(f"Reference: {component.reference}")
    print(f"Value: {component.value}")
```

## Running Tests

To run the tests for the component parser:

1. Ensure you have `pytest` installed:
   ```bash
   pip install pytest
   ```

2. Run the tests from the project root:
   ```bash
   pytest component_parser/test_component_parser.py
   ```

## Test Coverage

The test suite covers:
- Valid component name parsing
- Complex component name parsing
- Error cases for component names
- Basic and full component property parsing
- Error handling for invalid properties

## Development Notes

- Parsing is line-based and supports incremental error tracking
- Designed to be flexible with various KiCad schematic formats
- Part of the first phase in the SKiDL Parser Development Plan

## Future Improvements

- Support for more complex component properties
- Enhanced error reporting
- Integration with other parsing modules
