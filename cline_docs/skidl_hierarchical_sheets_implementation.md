# SKiDL Hierarchical Sheets Implementation Changes

## Key Code Changes Required

### 1. CircuitNode Class Updates
```python
@dataclass
class CircuitNode:
    """Represents a node in the circuit hierarchy"""
    instance_path: str          # Full path with numbers e.g. 'top.subckt0.child1'
    sheet_name: str            # Name for sheet file e.g. 'child'
    parent_path: Optional[str]  # Parent's full instance path or None for root
    children: List[str]        # Child instance paths
    parts: List['Part']        # Parts in this circuit instance
```

### 2. Path Handling Functions
Add new functions to separate concerns:
```python
def get_sheet_name(path: str) -> str:
    """Extract sheet name without numeric suffixes for file naming"""
    segments = path.split('.')
    last = segments[-1]
    if last == 'top':
        return last
    return re.sub(r'\d+$', '', last)

def get_instance_path(part) -> str:
    """Get full hierarchical instance path for part matching"""
    return getattr(part, 'hierarchy', 'top')
```

### 3. HierarchyManager Class Updates

#### Build Hierarchy Method
```python
def build_hierarchy(self, subcircuit_paths: List[str]) -> None:
    """Build hierarchy from subcircuit paths"""
    # Store valid instance paths
    self.valid_paths = set(subcircuit_paths)
    
    # Create nodes
    for path in subcircuit_paths:
        parts = path.split('.')
        parent = '.'.join(parts[:-1]) if len(parts) > 1 else None
        
        node = CircuitNode(
            instance_path=path,
            sheet_name=get_sheet_name(path),
            parent_path=parent,
            children=[],
            parts=[]
        )
        self.nodes[path] = node
    
    # Link children using instance paths
    for node in self.nodes.values():
        if node.parent_path and node.parent_path in self.nodes:
            parent = self.nodes[node.parent_path]
            parent.children.append(node.instance_path)
```

#### Part Assignment Method
```python
def assign_parts_to_circuits(self, circuit) -> None:
    """Assign parts to their circuit instances"""
    for part in circuit.parts:
        # Get instance path with numbers preserved
        instance_path = get_instance_path(part)
        
        # Find exact matching node
        if instance_path in self.nodes:
            node = self.nodes[instance_path]
            node.parts.append(part)
            logging.debug(f"Assigned part {part.ref} to node {node.instance_path}")
        else:
            logging.warning(f"No matching node for part {part.ref} at path {instance_path}")
```

#### Sheet Generation Method
```python
def _generate_circuit_schematic(self, node: CircuitNode, writer_class) -> None:
    """Generate schematic for a circuit node"""
    # Use sheet name (without numbers) for file
    out_path = self.project_dir / f"{node.sheet_name}.kicad_sch"
    
    if out_path.name in self.generated_files:
        return  # Sheet already exists
    
    # Create writer for this sheet
    writer = writer_class(str(out_path))
    
    # Add all parts from this instance
    grid_size = 20.0
    for idx, part in enumerate(node.parts):
        row = idx // 5
        col = idx % 5
        x = float(col * grid_size)
        y = float(-row * grid_size)
        
        writer.add_symbol_instance(self._create_symbol_instance(
            part, 
            position=(x, y)
        ))
    
    writer.generate()
    self.generated_files.add(out_path.name)
```

#### Sheet Symbol Creation
```python
def _create_sheet_symbol(self, node: CircuitNode, x: float, y: float) -> HierarchicalSheet:
    """Create sheet symbol for circuit instance"""
    sheet = HierarchicalSheet()
    
    # Position and size
    sheet.position = Position(f"{x}", f"{y}", "0")
    sheet.width = 30
    sheet.height = 20
    
    # Use instance path for display name
    sheet.sheetName = Property("Sheetname", node.instance_path)
    sheet.sheetName.position = Position(f"{x + sheet.width/2}", f"{y - 5}", "0")
    
    # Use sheet name (without numbers) for file reference
    sheet.fileName = Property("Sheetfile", f"{node.sheet_name}.kicad_sch")
    sheet.fileName.position = Position(f"{x + sheet.width/2}", f"{y - 2}", "0")
    
    return sheet
```

## Implementation Notes

1. **Path Handling**
- Instance paths (with numbers) used for:
  * Part assignment
  * Node identification
  * Parent-child relationships
  * Sheet symbol display names
- Sheet names (without numbers) used for:
  * Schematic file names
  * Sheet file references

2. **File Generation**
- One sheet file per unique circuit type
- Multiple instances reference same file
- Parts from all instances go to type's sheet

3. **Debug Logging**
Add logging to track:
- Instance path matching
- Sheet file generation
- Part assignments
- Sheet symbol creation

This implementation cleanly separates instance paths from sheet file naming while maintaining proper hierarchical relationships and part assignments.