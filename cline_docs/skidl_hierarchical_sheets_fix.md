# SKiDL Hierarchical Sheet Generation Fix

## Current Issue
The hierarchical sheet generation is failing to properly:
1. Assign parts to their circuit sheets
2. Maintain parent-child relationships between sheets
3. Handle multiple instances of the same circuit type

## Key Insight
Multiple instances of the same circuit type (e.g. single_resistor0, single_resistor1) should:
- Share a single schematic file (single_resistor.kicad_sch)
- Maintain unique paths for part assignment
- Reference the same sheet file in hierarchy symbols

## Required Changes

### 1. Separate Path Handling
We need two distinct path handling mechanisms:

1. **Part Assignment Paths**
- Must preserve numeric suffixes (e.g. single_resistor0)
- Used for matching parts to their specific circuit instance
- Maintains uniqueness for multiple instances

2. **Sheet File Paths**
- Should strip numeric suffixes (e.g. single_resistor0 -> single_resistor)
- Used for generating and referencing schematic files
- Allows multiple instances to share same sheet file

### 2. Path Matching Logic
Update path handling to:
```python
def get_sheet_name(path: str) -> str:
    """Get normalized sheet name without numeric suffixes"""
    segments = path.split('.')
    last = segments[-1]
    return re.sub(r'\d+$', '', last)

def get_instance_path(path: str) -> str:
    """Get full path with numeric suffixes preserved"""
    return path  # Keep original path with numbers
```

### 3. Sheet Generation Logic
Modify sheet generation to:
- Generate one sheet file per circuit type
- Allow multiple references to same sheet
- Track generated files by normalized name

```python
def _generate_circuit_schematic(self, node: CircuitNode, writer_class) -> None:
    """Generate schematic for a circuit node"""
    # Use normalized name for file
    sheet_name = get_sheet_name(node.full_path)
    out_path = self.project_dir / f"{sheet_name}.kicad_sch"
    
    if out_path.name in self.generated_files:
        return  # Sheet already exists
        
    # Create sheet with all parts from this instance
    writer = writer_class(str(out_path))
    for part in node.parts:
        writer.add_symbol_instance(...)
        
    writer.generate()
    self.generated_files.add(out_path.name)
```

### 4. Sheet Symbol References
Update sheet symbol creation to:
- Use normalized names for file references
- Preserve instance names for labels
- Handle multiple references to same sheet

```python
def _create_sheet_symbol(self, node: CircuitNode) -> None:
    sheet = HierarchicalSheet()
    
    # Use instance path for sheet name display
    sheet.sheetName = Property("Sheetname", node.full_path)
    
    # Use normalized path for file reference
    sheet_name = get_sheet_name(node.full_path)
    sheet.fileName = Property("Sheetfile", f"{sheet_name}.kicad_sch")
```

## Implementation Strategy

1. **Part Assignment**
- Keep original paths with numbers for matching
- Match parts to specific circuit instances
- Log detailed path matching information

2. **Sheet Generation**
- Generate sheets using normalized names
- Track generated sheets to avoid duplicates
- Ensure all parts from same circuit type go to same sheet

3. **Hierarchy Management**
- Maintain instance-specific paths in node structure
- Use normalized paths for file operations
- Keep parent-child relationships intact

## Testing Strategy

1. Test Cases:
- Multiple instances of same circuit type
- Nested hierarchies with repeated circuits
- Mixed unique and repeated circuits

2. Validation:
- Parts appear in correct shared sheets
- Sheet symbols reference correct files
- Instance names preserved in hierarchy
- No duplicate file generation

## Success Criteria

1. Parts correctly assigned to shared sheets
2. Sheet files generated once per circuit type
3. Multiple instances reference same sheet file
4. Hierarchy maintained with proper instance names
5. Clean sheet generation without errors

This revised approach separates instance path handling from sheet file naming, allowing multiple circuit instances to share schematic files while maintaining their unique identities in the hierarchy.