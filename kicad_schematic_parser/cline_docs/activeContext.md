# Current Task: Resolving KiCad Schematic Parser Test Failures

## Test Failures Overview
- Import statements were initially fixed by replacing 'skidl_kicad_parser' with 'kicad_hierarchy_parser'
- Remaining test failures in multiple test files:
  1. Net parsing not working correctly
  2. Pin position calculations seem incorrect
  3. Symbol definition and component pin extraction have issues
  4. Wire connection parsing not matching expected results

## Specific Test Failures
- `test_resistor_divider`: 'VIN' net not found
- `test_power_supply`: '3V3' net not found
- Pin position tests failing for various components
- Symbol definition parsing has a missing argument
- Component pin extraction returning empty dictionary

## Potential Areas of Investigation
- `component_parser.py`: Verify pin position calculation
- `net_parser.py`: Check net connectivity logic
- `wire_parser.py`: Validate wire connection parsing
- Verify compatibility with latest kiutils library

## Next Steps
1. Review and potentially modify `calculate_pin_position()` function
2. Check `find_symbol_definition()` method signature
3. Investigate why `get_component_pins()` is returning an empty dictionary
