# SKiDL Parser Development Plan

## Overview

Develop a Python parser to convert KiCad hierarchical netlists (hierarchy.txt format) into SKiDL Python code. Use a bottom-up approach starting with the smallest units (components) and building up to full hierarchical circuits.

## Development Phases

### Phase 1: Basic Component Parsing
1. Parse component library/name
   ```python
   # Input example
   Component: Device/R
   
   # Parser function
   def parse_component_name(line: str) -> Tuple[str, str]:
       """Parse library and component name."""
   ```

2. Parse component properties
   ```python
   # Input example
   Properties:
       Reference: R1
       Value: 10K
       Footprint: Resistor_SMD:R_0603_1608Metric
   
   # Parser function
   def parse_component_properties(lines: List[str]) -> Dict[str, str]:
       """Parse component properties."""
   ```

3. Create Component class
   ```python
   class Component:
       def __init__(self, lib: str, name: str, uuid: str = None):
           self.library = lib
           self.name = name
           self.uuid = uuid
           self.properties = {}
           self.original_file = None  # Store source file path
   ```

4. Generate SKiDL component code
   ```python
   def generate_component_code(component: Component) -> str:
       """Generate SKiDL code for a component."""
   ```

### Phase 2: Pin and Connection Parsing
1. Parse pin definitions
   ```python
   # Input example
   Pin 1 (5v_monitor):
       Position: (92.71, 54.61)
       Type: input
   
   # Parser function
   def parse_pin_definition(lines: List[str]) -> Dict[str, Any]:
       """Parse single pin definition."""
   ```

2. Parse pin connections
   ```python
   # Input example
   5v_monitor:
       Sheet_esp32s3mini1 Pin 1 (5v_monitor)
       Sheet_3v3_regulator Pin 1 (5v_monitor)
   
   # Parser function
   def parse_pin_connections(lines: List[str]) -> List[Tuple[str, str, str]]:
       """Parse pin connections."""
   ```

### Phase 3: Net Parsing
1. Parse net names
   ```python
   # Input example
   Local Labels:
       3v3_monitor at (137.16, 60.96)
   
   # Parser function
   def parse_net_names(lines: List[str]) -> List[str]:
       """Parse net names."""
   ```

2. Create Net class
   ```python
   class Net:
       def __init__(self, name: str):
           self.name = name
           self.pins = []
           self.type = None  # power, signal, hierarchical
   ```

### Phase 4: Sheet Structure Parsing
1. Parse file boundaries
   ```python
   # Input example
   ******* Analyzing: example_kicad_project/power2.kicad_sch *******
   
   # Parser function
   def parse_file_boundary(line: str) -> str:
       """Parse file name from boundary marker."""
   ```

2. Parse sheet definitions
   ```python
   # Input example
   Sheet: 3v3_regulator
       File: power2.kicad_sch
       UUID: 7a16d2b9-1ea1-4c05-9c09-25544e050e50
   
   # Parser function
   def parse_sheet_definition(lines: List[str]) -> Dict[str, str]:
       """Parse sheet definition including UUID."""
   ```

3. Create Sheet class
   ```python
   class Sheet:
       def __init__(self, name: str, filename: str, uuid: str):
           self.name = name
           self.filename = filename
           self.uuid = uuid
           self.components = []
           self.nets = []
           self.parent = None
           self.docstring = f"Original file: {filename}"
   ```

### Phase 5: Hierarchy Building
1. Parse parent relationships
   ```python
   # Input example
   Parent Sheet: example_kicad_project/example_kicad_project.kicad_sch
   
   # Parser function
   def parse_parent_relationship(line: str) -> str:
       """Parse parent sheet name."""
   ```

2. Build sheet tree
   ```python
   def build_sheet_hierarchy(sheets: List[Sheet], parent_relationships: List[Tuple[str, str]]) -> Sheet:
       """Build sheet hierarchy tree."""
   ```

### Phase 6: SKiDL Code Generation
1. Generate subcircuit functions
   ```python
   def generate_subcircuit(sheet: Sheet) -> str:
       """Generate SKiDL subcircuit function for a sheet."""
       return f"""
       @subcircuit
       def {sheet.name}():
           \"""{sheet.docstring}\"""
           # Components
           {generate_components(sheet.components)}
           # Nets
           {generate_nets(sheet.nets)}
           # Connections
           {generate_connections(sheet.connections)}
       """
   ```

2. Generate full circuit
   ```python
   def generate_circuit(root_sheet: Sheet) -> str:
       """Generate complete SKiDL circuit code."""
   ```

## Testing Strategy

Create a single test file with incremental tests:

```python
def test_component_name_parsing():
    """Test parsing component library and name."""
    line = "Component: Device/R"
    lib, name = parse_component_name(line)
    assert lib == "Device"
    assert name == "R"

def test_component_properties():
    """Test parsing component properties."""
    ...
```

## Error Handling

Create simple line-based error tracking:

```python
class ParseError:
    def __init__(self, line_num: int, line: str, message: str):
        self.line_num = line_num
        self.line = line
        self.message = message
        
class ParseResult:
    def __init__(self):
        self.success = True
        self.errors = []
        self.data = None
    
    def add_error(self, line_num: int, line: str, message: str):
        self.errors.append(ParseError(line_num, line, message))
        self.success = False
```

## Implementation Order

1. Start with simplest component parsing
2. Add property parsing
3. Add pin parsing
4. Add net parsing
5. Add sheet structure parsing
6. Add hierarchy building
7. Add SKiDL code generation

Each step should:
1. Implement parser function
2. Add tests
3. Add error handling
4. Generate corresponding SKiDL code

## Usage Example

```python
# Parse hierarchy file
parser = SkidlParser("hierarchy.txt")
result = parser.parse()

# Check for errors
if result.errors:
    for error in result.errors:
        print(f"Line {error.line_num}: {error.message}")
        print(f"Content: {error.line}")

# Generate code if successful
if result.success:
    skidl_code = parser.generate_skidl_code()
    with open("output.py", "w") as f:
        f.write(skidl_code)
```