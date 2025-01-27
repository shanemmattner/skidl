# SKiDL Hierarchical Sheet Layout Improvements

## Project Context
- Location: src/skidl/tools/kicad8/gen_schematic.py
- Purpose: Generates KiCad schematics from SKiDL circuit descriptions
- Specific Focus: Hierarchical sheet layout in top-level schematic

## Original Implementation
- Sheet dimensions: 40x40mm
- Spacing: 20mm between sheets
- Layout: Grid pattern with 2 sheets per row
- Issues:
  - Sheets too large
  - Poor spacing
  - Not centered on page
  - Labels positioned at (0,0)

## Changes Made
1. Sheet Size Reduction
   - Width/Height: 30mm (reduced from 40mm)
   - Purpose: More compact representation while maintaining readability

2. Spacing Increase
   - New spacing: 40mm (increased from 20mm)
   - Purpose: Better visual separation between sheets

3. Page Centering
   - Added calculations for A4 page (297x210mm)
   - Computes total width/height needed
   - Centers sheet group on page
   - Implementation:
     ```python
     total_width = num_cols * sheet_width + (num_cols - 1) * spacing
     total_height = num_rows * sheet_height + (num_rows - 1) * spacing
     start_x = (297 - total_width) / 2  # A4 width
     start_y = (210 - total_height) / 2  # A4 height
     ```

4. Label Positioning
   - Sheet name: 5mm above sheet
   - File name: 2mm below sheet name
   - Both centered horizontally relative to sheet
   - Implementation:
     ```python
     sheet.sheetName.position.X = str(x + sheet_width/2)
     sheet.sheetName.position.Y = str(y - 5)
     sheet.fileName.position.X = str(x + sheet_width/2)
     sheet.fileName.position.Y = str(y - 2)
     ```

## Technical Details
- Uses kiutils library for KiCad file manipulation
- Maintains hierarchical structure with main schematic + subcircuit sheets
- Automatically creates blank schematics for each subcircuit
- Centers content considering A4 page dimensions

## Key Files
- gen_schematic.py: Main implementation
- Location: src/skidl/tools/kicad8/
- Dependencies: kiutils for KiCad file handling

## Future Considerations
- May need adjustments for different page sizes
- Could add configuration options for sheet dimensions/spacing
- Consider adding grid snapping for cleaner alignment
