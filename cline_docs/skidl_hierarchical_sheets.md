# SKiDL Hierarchical Sheet Generation Analysis

## Current Behavior

The hierarchical schematic generation is not properly handling nested circuits. While the SKiDL Circuit object correctly tracks the hierarchy in its group_name_cntr:

```python
'group_name_cntr': Counter({
    'top.single_resistor': 1,
    'top.single_resistor0.two_resistors_circuit': 1
})
```

The generated KiCad schematics show both circuits at the top level instead of maintaining the proper parent-child relationship.

## Key Files

1. test_circuits.py - Shows the circuit definition with intended hierarchy:
   ```python
   @SubCircuit
   def single_resistor():
       r1 = Part("Device", "R", ...)
       two_resistors_circuit()  # Called as child circuit

   @SubCircuit
   def two_resistors_circuit():
       r2 = Part("Device", "R", ...)
       r3 = Part("Device", "R", ...)
   ```

2. gen_schematic_v8.py - Main schematic generation logic:
   - Correctly identifies subcircuits from group_name_cntr.keys()
   - Creates separate .kicad_sch files for each subcircuit
   - Issue: When adding hierarchical sheets (lines 222-249), treats all subcircuits as top-level

3. kicad_writer.py - Handles the actual schematic file writing:
   - Creates symbol definitions and instances
   - Currently doesn't have hierarchy-aware sheet creation

## Issue Analysis

1. Hierarchy Information:
   - SKiDL correctly tracks circuit hierarchy in group_name_cntr
   - Circuit names contain hierarchy info: 'top.single_resistor0.two_resistors_circuit'
   - This hierarchy is not being used when creating KiCad sheet symbols

2. Sheet Symbol Creation:
   - Current code places all sheets in a grid layout
   - No parent-child relationships are established
   - Sheets need to be nested according to the circuit hierarchy

3. Project Configuration:
   - sheets[] array in .kicad_pro needs to reflect proper hierarchy
   - Sheet paths should indicate parent-child relationships

## Suggested Solution

1. Parse Hierarchy:
   ```python
   def parse_circuit_hierarchy(group_names):
       hierarchy = {}
       for path in group_names:
           parts = path.split('.')
           current = hierarchy
           for part in parts[1:]:  # Skip 'top'
               if part not in current:
                   current[part] = {}
               current = current[part]
       return hierarchy
   ```

2. Create Hierarchical Sheets:
   - Modify sheet creation to follow parsed hierarchy
   - Place child sheets within parent sheets
   - Update sheet paths to reflect nesting

3. Update Project Configuration:
   - Modify sheets[] array to include parent information
   - Use proper sheet paths for hierarchical navigation

## Required Changes

1. gen_schematic_v8.py:
   - Add hierarchy parsing function
   - Modify sheet symbol creation to respect hierarchy
   - Update sheet paths in project configuration

2. kicad_writer.py:
   - Add support for hierarchical sheet creation
   - Include parent sheet information in sheet symbols

## Testing Strategy

1. Create test cases with various hierarchy levels
2. Verify sheet symbols are properly nested
3. Confirm KiCad can navigate the hierarchy correctly
4. Check sheet paths in project configuration

## Next Steps

1. Implement hierarchy parsing
2. Modify sheet symbol creation
3. Update project configuration handling
4. Add test cases for hierarchical sheets
5. Document the new hierarchical sheet handling
