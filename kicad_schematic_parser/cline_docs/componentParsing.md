# Component Parsing and Deduplication

## Overview
This document captures the implementation details of our component parsing strategy, with a focus on handling duplicate components.

## Parsing Strategy
- Components are parsed from KiCad schematic files
- Parsing includes:
  * Library and component name extraction
  * Properties parsing (Reference, Value, Footprint, etc.)
  * Position and angle information

## Duplicate Component Handling
### Detection Mechanism
- Global dictionary `_COMPONENT_REFERENCES` tracks component references
- Duplicate detection occurs during parsing
- Logging and warning system for duplicate components

### Duplicate Rules
- First occurrence of a component reference is preserved
- Subsequent components with the same reference trigger:
  * Warning log message
  * ParseResult error addition
  * Preservation of first component's details

### Logging
- Uses Python's `logging` module
- Warning level logging
- Timestamp and detailed message for each duplicate

## Implementation Details
- Located in: `src/skidl_generator/component_parser/component_parser.py`
- Key methods:
  * `parse_component_block()`
  * `parse_component_name()`
  * `parse_component_properties()`

## Future Improvements
- Configurable duplicate handling strategies
- More granular duplicate detection (e.g., partial match)
- Enhanced logging and reporting
