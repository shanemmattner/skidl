# System Architecture

## Core Modules
1. KiCad Hierarchy Parser
   - Responsible for parsing KiCad schematic files
   - Extracts component, pin, and connection information
   - Handles wire connections and net analysis
   - Processes different types of schematic labels

2. SKiDL Generator
   - Converts text representation to SKiDL Python code
   - Modular approach with six distinct parsing phases:
     * Component Parsing
     * Pin Parsing
     * Net Parsing
     * Sheet Parsing
     * Hierarchy Building
     * Code Generation

## Parsing Stages Detailed
### Component Parsing (Current Status: Complete)
- Extracts component properties
- Validates component data format
- Handles library and component name parsing
- Captures reference, value, and other properties

### Planned Parsing Stages
1. Pin Parsing
   - Track pin electrical types
   - Manage pin positions
   - Handle pin-to-pin connections

2. Net Parsing
   - Parse net names and connections
   - Handle power, local, and hierarchical nets
   - Track net connectivity

3. Sheet Parsing
   - Parse sheet definitions and boundaries
   - Manage sheet properties and metadata
   - Track parent-child sheet relationships

4. Hierarchy Building
   - Construct complete circuit hierarchy
   - Resolve cross-sheet connections

5. Code Generation
   - Generate SKiDL Python code
   - Create subcircuit functions
   - Handle component instantiation

## Key Design Patterns
- Modular Architecture
- Separation of Concerns
- Incremental Parsing
- Test-Driven Development
- Phased Implementation Strategy

## Error Handling Considerations
- Graceful handling of parsing limitations
- Detailed error reporting
- Support for manual verification and correction
- Flexible parsing with success/failure results
