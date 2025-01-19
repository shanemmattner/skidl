# KiCad Schematic Pin Position Analyzer

This project provides tools for analyzing KiCad schematic files to extract and verify component pin positions. It uses the `kiutils` library to parse KiCad schematic files and calculate absolute pin positions for all components.

## Overview

The main script (`kiutils_test.py`) analyzes KiCad schematic files to:
1. Extract component pin positions
2. Calculate absolute coordinates for each pin
3. Determine pin electrical types
4. Output detailed pin information for each component

This is particularly useful for:
- Verifying component placement and orientation
- Extracting pin position data for PCB layout tools
- Automated schematic analysis
- Regression testing of schematic modifications

## How It Works

### Coordinate System

The script handles KiCad's coordinate system where:
- Origin is at the component center
- Y axis points up (negative in KiCad coordinates)
- X axis points right (positive)
- Pin positions are relative to their component's center
- Final coordinates are in KiCad's global coordinate space

### Key Functions

#### `calculate_pin_position(component_position, pin_position, component_angle=0)`
Calculates a pin's absolute position based on:
- Component's position (center point)
- Pin's relative position
- Component's rotation angle
- KiCad's coordinate system conventions

The calculation:
1. Applies rotation to the pin's relative coordinates
2. Adds the component's position
3. Adjusts for KiCad's coordinate system (Y-axis negation)

#### `find_symbol_definition(schematic, lib_nickname, entry_name)`
Locates a component's symbol definition in the schematic's library symbols.

#### `get_component_pins(schematic)`
Extracts pin information for all components:
1. Finds each component's symbol definition
2. Gets pin data from the symbol's units
3. Calculates absolute positions
4. Sorts pins by pin number
5. Returns a dictionary mapping component references to their pin information

#### `analyze_schematic(schematic)`
Main analysis function that:
1. Extracts all component pin data
2. Prints formatted results including:
   - Component references
   - Pin numbers and names
   - Absolute positions
   - Electrical types

## Usage

### Basic Usage

```bash
python kiutils_test.py <schematic_file_path>
```

Example:
```bash
python kiutils_test.py example_kicad_project/power2.kicad_sch
```

This will output pin position information for all components in the schematic.

### Running Tests

The project includes comprehensive regression tests that verify pin positions against known-good values.

Setup:
```bash
# Install required packages
pip install pytest kiutils

# Run tests
python -m pytest tests/ -v
```

The tests verify:
1. Power supply schematic (power2.kicad_sch)
   - Voltage regulator pins
   - Capacitor positions
   - Power symbols
2. Resistor divider schematic (resistor_divider.kicad_sch)
   - Resistor pin positions
   - Capacitor positions
3. STM32 schematic (stm32.kicad_sch)
   - Complex microcontroller pinout
   - Connector positions
   - Power and peripheral connections

## Project Structure

```
.
├── kiutils_test.py          # Main analysis script
├── tests/
│   ├── conftest.py         # Pytest configuration
│   ├── test_pin_positions.py # Test cases
│   ├── power2.kicad_sch    # Test schematics
│   ├── resistor_divider.kicad_sch
│   └── stm32.kicad_sch
└── *_output.txt            # Sample outputs for verification
```

## Dependencies

- Python 3.x
- kiutils: KiCad file format parser
- pytest: For running tests

## Common Use Cases

1. **Schematic Verification**
   - Verify component pin positions after schematic changes
   - Check for accidental component rotations
   - Validate power connections

2. **Automated Analysis**
   - Extract pin positions for external tools
   - Generate connection reports
   - Verify design rules

3. **Regression Testing**
   - Ensure schematic modifications don't affect pin positions
   - Verify component orientations remain correct
   - Test against known-good reference positions

## Notes

- Pin positions are in KiCad's coordinate system (millimeters)
- Y coordinates are negated in the final output to match KiCad's convention
- Pin numbers are sorted numerically for consistent output
- A tolerance of 0.01 (1%) is used for position comparisons in tests
