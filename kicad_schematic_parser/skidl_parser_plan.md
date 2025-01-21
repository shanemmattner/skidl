# SKiDL Parser Development Plan

## Overview

The goal is to develop Python code that can parse a text file describing a kicad project and generate equivalent SKiDL code. The circuit text file contains information about sheets, components, pins, labels, and netlist connections that need to be converted into SKiDL's Python-based circuit description format.

## Key Features Needed

1. Sheet Processing
   - Parse sheet definitions from circuit text file
   - Create Python subcircuit functions for each sheet
   - Handle sheet hierarchy (parent-child relationships)
   - Process sheet pins as function parameters

2. Component Processing
   - Parse component definitions
   - Extract key properties:
     - Library and part name
     - Reference designator
     - Value
     - Footprint
     - Description
   - Create SKiDL Part objects with correct parameters

3. Net Processing
   - Parse net definitions
   - Handle different net types:
     - Power nets (VCC, GND, etc.)
     - Signal nets
     - Hierarchical nets between sheets
   - Create SKiDL Net objects
   - Process net connections between components

4. Pin Connection Processing
   - Parse pin definitions
   - Handle pin types (input, output, bidirectional, etc.)
   - Connect pins to nets
   - Support pin arrays and buses

## Development Phases

### Phase 1: Basic Structure
1. Create parser class structure
2. Implement file reading and section identification
3. Create data structures to hold parsed information

### Phase 2: Sheet Processing
1. Implement sheet section parser
2. Create sheet object model
3. Generate subcircuit function templates
4. Handle sheet parameters (pins)

### Phase 3: Component Processing
1. Implement component section parser
2. Create component object model
3. Generate SKiDL Part creation code
4. Handle component properties

### Phase 4: Net Processing
1. Implement net section parser
2. Create net object model
3. Generate SKiDL Net creation code
4. Handle power nets

### Phase 5: Connection Processing
1. Implement pin connection parser
2. Create connection object model
3. Generate SKiDL connection code
4. Handle hierarchical connections

### Phase 6: Code Generation
1. Implement SKiDL code generator
2. Generate complete circuit description
3. Handle imports and dependencies
4. Format output code

## Implementation Details

### Parser Class Structure
```python
class SkidlParser:
    def __init__(self, hierarchy_file):
        self.hierarchy_file = hierarchy_file
        self.sheets = {}
        self.components = {}
        self.nets = {}
        
    def parse(self):
        # Main parsing logic
        pass
        
    def parse_sheets(self):
        # Sheet parsing logic
        pass
        
    def parse_components(self):
        # Component parsing logic
        pass
        
    def parse_nets(self):
        # Net parsing logic
        pass
        
    def generate_skidl_code(self):
        # Code generation logic
        pass
```

### Sheet Object Model
```python
class Sheet:
    def __init__(self, name, filename, uuid):
        self.name = name
        self.filename = filename
        self.uuid = uuid
        self.pins = []
        self.components = []
        self.nets = []
        self.parent = None
        self.children = []
```

### Component Object Model
```python
class Component:
    def __init__(self, library, name, reference):
        self.library = library
        self.name = name
        self.reference = reference
        self.value = None
        self.footprint = None
        self.pins = []
        self.sheet = None
```

### Net Object Model
```python
class Net:
    def __init__(self, name):
        self.name = name
        self.pins = []
        self.type = None  # power, signal, hierarchical
        self.sheet = None
```

## Testing Strategy

1. Unit Tests
   - Test individual parser components
   - Test object model creation
   - Test code generation

2. Integration Tests
   - Test complete parsing workflow
   - Test hierarchical circuit parsing
   - Test complex net connections

3. Validation Tests
   - Compare generated SKiDL code output with expected results
   - Verify netlist equivalence
   - Test with various input complexities

## Example Usage

```python
# Parse hierarchy file and generate SKiDL code
parser = SkidlParser("hierarchy.txt")
parser.parse()
skidl_code = parser.generate_skidl_code()

# Write SKiDL code to file
with open("output.py", "w") as f:
    f.write(skidl_code)
```

## Next Steps

1. Implement basic parser structure
2. Create test hierarchy files of varying complexity
3. Implement sheet parsing
4. Add component parsing
5. Add net parsing
6. Implement code generation
7. Add validation and testing
8. Document usage and examples
