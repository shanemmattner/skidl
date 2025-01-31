# SKiDL Hierarchical Sheet Generation - Current Status

## Progress Made
Fixed several aspects of hierarchical sheet generation:

1. Part Assignment
- R1 correctly appears in single_resistor.kicad_sch
- R2 and R3 correctly appear in two_resistors_circuit.kicad_sch
- Parts are positioned properly within their sheets

2. File Generation
- Generates separate sheets for each circuit type
- Preserves component properties and positions
- Creates proper sheet symbols in top-level schematic

## Remaining Issue: Missing Sheet Symbol

The hierarchy is not complete because single_resistor.kicad_sch does not contain a sheet symbol referencing two_resistors_circuit.kicad_sch.

### Current Output

1. Top Level (testing_hierarchy.kicad_sch)
```
(sheet (at 100 50) (size 30 20)
  (property "Sheetname" "top.single_resistor")
  (property "Sheetfile" "single_resistor.kicad_sch")
)
```

2. Single Resistor Sheet (single_resistor.kicad_sch)
- Contains R1 component ✓
- Missing sheet symbol for two_resistors_circuit ✗

3. Two Resistors Sheet (two_resistors_circuit.kicad_sch)
- Contains R2 and R3 components ✓
- Positioned correctly at (0,0) and (20,0) ✓

### Required Fix

Need to modify _generate_circuit_schematic() to:
1. Check for child circuits
2. Add sheet symbols for each child circuit
3. Update the schematic to include these sheet symbols

Example of missing sheet symbol that should be in single_resistor.kicad_sch:
```kicad
(sheet (at 100 50) (size 30 20)
  (property "Sheetname" "two_resistors_circuit")
  (property "Sheetfile" "two_resistors_circuit.kicad_sch")
)
```

## Next Steps

1. Update HierarchyManager to:
- Track parent-child relationships properly
- Add sheet symbols for child circuits
- Update schematic files with sheet symbols

2. Modify sheet generation to:
- Check for child circuits
- Create and position sheet symbols
- Update parent schematic files

3. Add debug logging for:
- Parent-child relationships
- Sheet symbol creation
- Schematic updates

## Implementation Notes

The fix will require changes to:

1. CircuitNode class
```python
@dataclass
class CircuitNode:
    instance_path: str
    sheet_name: str
    parent_path: Optional[str]
    children: List[str]  # Need to properly populate this
    parts: List['Part']
```

2. Sheet Generation
```python
def _generate_circuit_schematic(self, node: CircuitNode, writer_class) -> None:
    # Current: Adds parts correctly
    # Need to add: Sheet symbol creation for children
    for child_path in node.children:
        child = self.nodes[child_path]
        sheet = self._create_sheet_symbol(child, x, y)
        # Add sheet to parent schematic
```

3. Hierarchy Building
```python
def build_hierarchy(self, subcircuit_paths: List[str]) -> None:
    # Current: Creates nodes correctly
    # Need to improve: Parent-child relationship tracking
    for path in subcircuit_paths:
        parts = path.split('.')
        parent = '.'.join(parts[:-1]) if len(parts) > 1 else None
        # Ensure proper parent-child linking
```

This documentation will be used to guide the implementation of the remaining fixes in a new task.