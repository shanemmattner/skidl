## Parser Architecture

### Overall Structure
- Modular parsing approach with separate modules for different parsing concerns
- Located in: `src/kicad_hierarchy_parser/`

### Key Parsing Modules
1. Components Parsing
   - Path: `src/kicad_hierarchy_parser/components/component_parser.py`
   - Responsible for extracting and processing individual component details

2. Connectivity Parsing
   - Path: `src/kicad_hierarchy_parser/connectivity/`
   - Submodules:
     - `net_parser.py`: Handles net-related parsing
     - `wire_parser.py`: Processes wire connections

3. Labels Parsing
   - Path: `src/kicad_hierarchy_parser/labels/label_parser.py`
   - Manages parsing of local and global labels

### Parsing Strategy
- Bottom-up approach
- Start with smallest units (components)
- Progressively build more complex structures

### Error Handling
- Line-based error tracking
- Comprehensive error collection mechanism
- Allows for partial parsing and error reporting

### Code Generation
- Separate module for SKiDL code generation
- Located in: `src/skidl_generator/`
- Modular approach with separate parsers for:
  - Components
  - Hierarchy
  - Nets
  - Pins

### Testing Approach
- Comprehensive unit testing
- Incremental test development
- Focus on parsing accuracy and error handling
