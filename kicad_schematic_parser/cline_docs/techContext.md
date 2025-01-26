## Technical Context for Net Parsing

### Technology Stack
- Python 3.13.1
- Pytest 8.3.4
- KiCad Schematic Parsing
- kiutils Library

### Key Technical Constraints
- Parsing KiCad hierarchical schematics
- Maintaining compatibility with SKiDL generator
- Handling complex multi-sheet designs

### Parsing Approach
- Recursive hierarchical parsing
- Priority-based label resolution
- Flexible net formation algorithm

### Net Naming Implementation
- Strict priority hierarchy:
  1. Sheet Pins
  2. Hierarchical Labels
  3. Power Labels
  4. Local Labels
  5. Generated ID
- Preserves all label information
- Maintains connectivity across sheets

### Testing Strategy
- Snapshot-based testing
- Minimal test case generation
- Focused on reproducibility
- Comprehensive coverage of:
  - Resistor divider circuits
  - Multi-rail power supplies
  - Complex hierarchical designs

### Module Dependencies
- `src/kicad_hierarchy_parser/`
  * `connectivity/net_parser.py`
  * `labels/label_parser.py`
  * `components/component_parser.py`

### Performance Considerations
- Minimize recursive call overhead
- Implement efficient caching mechanisms
- Use generator functions for memory efficiency

### Development Environment
- macOS development platform
- Python virtual environment
- Continuous integration with Pytest
- Version control: Git

### Optimization Strategies
- Lazy evaluation of net connections
- Memoization of parsing results
- Parallel processing for large schematics

### Future Improvements
- Implement more robust error handling
- Add comprehensive logging
- Create detailed documentation for parsing logic
- Support for advanced KiCad schematic features
