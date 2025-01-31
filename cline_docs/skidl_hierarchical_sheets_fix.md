# SKiDL Hierarchical Sheets Fix Status

## Current Progress

1. Fixed hierarchical sheet generation:
   - Sheet symbols are properly added to parent schematics
   - Sheet names are correctly formatted without full paths
   - Sheet instances have proper project paths

2. Fixed s-expression formatting:
   - Added quotes around version numbers
   - Fixed property formatting with effects blocks
   - Added proper instances blocks

## Remaining Issues

1. Test failures in test_blank_sch.py:
   - Generated version is 20211014
   - Expected version is 20231120
   - Issue appears to be with template files or version inheritance

## Next Steps

1. Need to investigate why test_blank_sch.py is getting old version:
   - Check all template files for version numbers
   - Verify version inheritance in gen_schematic_v8.py
   - Ensure version is properly set in all test scenarios

2. Update test suite:
   - Fix version number mismatches
   - Update reference files if needed
   - Add more debug logging to track version inheritance

## Implementation Details

1. Version number locations:
   - KicadSchematicWriter.version = "20231120"
   - Reference files have version "20231120"
   - Tests expect version "20231120"
   - But test_blank_sch.py gets "20211014"

2. File hierarchy:
   - src/skidl/tools/kicad8/sch_gen/kicad_writer.py
   - src/skidl/tools/kicad8/sch_gen/hierarchy_manager.py
   - src/skidl/tools/kicad8/sch_gen/tests/test_blank_sch.py
   - src/skidl/tools/kicad8/sch_gen/tests/reference_schematics/

## Debug Notes

1. Test output shows:
```
AssertionError: Incorrect schematic version
assert '20211014' == '20231120'
```

2. Hierarchy is working:
```
[HIERARCHY ] Node: top.single_resistor
[HIERARCHY ]   Sheet name: single_resistor
[HIERARCHY ]   Parent: top
[HIERARCHY ]   Children: ['top.single_resistor0.two_resistors_circuit']
```

## Next Task

Create a new task to:
1. Find where 20211014 version is coming from
2. Update all template files to use 20231120
3. Fix version inheritance in test environment
4. Update test reference files if needed