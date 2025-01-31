# SKiDL Hierarchical Sheet Generation Fix - Summary

## Problem Solved
Fixed hierarchical sheet generation to properly:
1. Assign parts to their correct circuit sheets
2. Maintain parent-child relationships between sheets
3. Handle multiple instances of the same circuit type

## Key Changes

### 1. Path Handling Separation
- Instance paths (with numbers) for part matching
  * Example: top.single_resistor0
  * Used to match parts to specific circuit instances
- Sheet names (without numbers) for file generation
  * Example: single_resistor.kicad_sch
  * Used for sheet file names and references

### 2. Part Assignment
- Improved path matching to handle both exact and normalized matches
- Parts are correctly assigned to their circuit instances
- Multiple instances of same circuit share one sheet file

### 3. Sheet Generation
- Generates one sheet file per circuit type
- Maintains proper sheet references
- Preserves hierarchy relationships

## Example Output

### 1. Top Level (testing_hierarchy.kicad_sch)
```
(sheet (at 100 50) (size 30 20)
  (property "Sheetname" "top.single_resistor")
  (property "Sheetfile" "single_resistor.kicad_sch")
)
```

### 2. Single Resistor Sheet (single_resistor.kicad_sch)
- Contains R1 component
- References two_resistors_circuit.kicad_sch

### 3. Two Resistors Sheet (two_resistors_circuit.kicad_sch)
- Contains R2 and R3 components
- Positioned correctly at (0,0) and (20,0)

## Verification
Debug output confirms:
```
Processing part R1:
  Instance path: top.single_resistor0
  Assigned to matching node: top.single_resistor
  Sheet file will be: single_resistor.kicad_sch

Processing part R2:
  Instance path: top.single_resistor0.two_resistors_circuit0
  Assigned to matching node: top.single_resistor0.two_resistors_circuit
  Sheet file will be: two_resistors_circuit.kicad_sch
```

## Key Implementation Details

1. CircuitNode Class
```python
@dataclass
class CircuitNode:
    instance_path: str    # Full path with numbers
    sheet_name: str      # Name for sheet file
    parent_path: Optional[str]
    children: List[str]
    parts: List['Part']
```

2. Path Handling
```python
def get_sheet_name(path: str) -> str:
    """Extract sheet name without numeric suffixes"""
    segments = path.split('.')
    last = segments[-1]
    if last == 'top':
        return last
    return re.sub(r'\d+$', '', last)
```

3. Part Assignment
```python
# Try exact match first
if instance_path in self.nodes:
    node = self.nodes[instance_path]
    node.parts.append(part)
    
# Fall back to normalized matching
base_path = '.'.join(get_sheet_name(segment) 
    for segment in instance_path.split('.'))
matching_nodes = [
    node for node in self.nodes.values()
    if '.'.join(get_sheet_name(segment) 
        for segment in node.instance_path.split('.')) == base_path
]
```

## Success Criteria Met
✓ All parts appear on their intended sheets
✓ Hierarchy matches SKiDL's circuit structure
✓ Sheet symbols correctly reference child sheets
✓ No path normalization warnings
✓ Clean sheet generation without errors