# SKiDL Hierarchical Sheet Implementation Guide

## Current Implementation Analysis

After analyzing the reference implementation and current code, here are the key findings:

### Reference Implementation (test_nested_project.py)

1. Sheet Structure:
```kicad_sch
(sheet
    (at 125.73 66.04)
    (size 13.97 15.24)
    (property "Sheetname" "single_resistor")
    (property "Sheetfile" "single_resistor.kicad_sch")
    (instances
        (project "nested_project"
            (path "/3a480dbf-5a3c-4b90-9d48-bbf5b4cbfeef"
                (page "2")
            )
        )
    )
)
```

2. Sheet Instances:
```kicad_sch
(sheet_instances
    (path "/"
        (page "1")
    )
)
```

### Current Implementation Issues

1. Hierarchy Tracking:
   - SKiDL correctly tracks hierarchy in group_name_cntr:
     ```python
     {
         'top.single_resistor': 1,
         'top.single_resistor0.two_resistors_circuit': 1
     }
     ```
   - But gen_schematic_v8.py doesn't use this hierarchy when creating sheets

2. Sheet Creation (gen_schematic_v8.py):
   ```python
   # Current code places all sheets at top level
   for subcircuit_path in subcircuits:
       subcircuit_name = subcircuit_path.split('.')[-1]
       # Creates sheet without considering parent-child relationship
   ```

## Required Changes

1. Hierarchy Parsing in gen_schematic_v8.py:
```python
def parse_circuit_hierarchy(subcircuits):
    """Convert flat subcircuit paths into nested hierarchy dict."""
    hierarchy = {}
    for path in subcircuits:
        parts = path.split('.')
        current = hierarchy
        for i, part in enumerate(parts[1:]):  # Skip 'top'
            if i == len(parts[1:]) - 1:
                current[part] = None  # Leaf node
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
    return hierarchy
```

2. Sheet Creation:
```python
def create_sheet_hierarchy(hierarchy, parent_path="/"):
    """Create hierarchical sheets recursively."""
    sheets = []
    for name, children in hierarchy.items():
        sheet = HierarchicalSheet()
        sheet.sheetName = Property(key="Sheetname", value=name)
        sheet.fileName = Property(key="Sheetfile", value=f"{name}.kicad_sch")
        
        # Set sheet path based on parent
        sheet_path = f"{parent_path}/{name}"
        sheet.instances = [
            {
                "path": sheet_path,
                "page": str(len(sheets) + 2)  # Start from page 2
            }
        ]
        
        # Recursively handle children
        if children:
            child_sheets = create_sheet_hierarchy(children, sheet_path)
            sheets.extend(child_sheets)
            
        sheets.append(sheet)
    return sheets
```

3. Project Configuration:
```python
def update_project_config(config, hierarchy, parent_path="/"):
    """Update project config with hierarchical sheet paths."""
    sheets = []
    for name, children in hierarchy.items():
        sheet_path = f"{parent_path}/{name}"
        sheets.append({
            "path": f"{name}.kicad_sch",
            "sheet_name": name,
            "id": str(uuid.uuid4()),
            "parent_path": parent_path
        })
        if children:
            sheets.extend(update_project_config(config, children, sheet_path))
    return sheets
```

## Implementation Steps

1. Modify gen_schematic_v8.py:
   - Add hierarchy parsing function
   - Update sheet creation to use hierarchy
   - Modify project configuration update

2. Update KicadSchematicWriter:
   - Add support for sheet instances with proper paths
   - Include parent-child relationships in sheet properties

3. Testing:
   - Use test_circuits.py as test case
   - Verify sheet hierarchy in KiCad
   - Check sheet paths and navigation

## Expected Result

1. Main Schematic (testing_hierarchy.kicad_sch):
   - Contains single_resistor sheet
   - Proper sheet path and instance configuration

2. Single Resistor Sheet (single_resistor.kicad_sch):
   - Contains two_resistors_circuit sheet
   - Maintains parent-child relationship

3. Project Configuration:
   - Correct sheet paths reflecting hierarchy
   - Proper parent-child relationships
   - Working sheet navigation in KiCad

## Verification Steps

1. Generate test schematic:
   ```python
   single_resistor()  # Creates nested hierarchy
   generate_schematic(
       filepath="hierarchy_test",
       project_name="testing_hierarchy"
   )
   ```

2. Check KiCad schematic:
   - Open in KiCad
   - Verify sheet hierarchy
   - Test navigation between sheets

3. Verify file structure:
   - Check sheet paths in .kicad_pro
   - Verify sheet instance configurations
   - Confirm parent-child relationships