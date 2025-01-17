# SKiDL Schematic Generation Analysis

## Overview

SKiDL's schematic generation converts a Circuit object into a KiCad schematic file. The current implementation focuses heavily on component placement and routing, making it complex and brittle. A simpler approach using net labels instead of explicit wire routing would be more maintainable and compatible with newer KiCad versions.

## Current Implementation Analysis

### Core Files and Classes

1. `gen_schematic.py` (Main Entry Point)
   - Function: `gen_schematic()` (line ~580)
   - Responsible for:
     - Circuit preprocessing
     - Node hierarchy creation
     - Placement initiation
     - Routing initiation 
     - KiCad file generation

2. `node.py`
   - Class: `Node`
   - Primary container for circuit hierarchy
   - Handles:
     - Component organization
     - Hierarchical structure
     - Placement coordination
     - Routing coordination

3. `place.py`
   - Class: `Placer` (mixin)
   - Complex placement algorithms including:
     - Force-directed placement
     - Component grouping
     - Block placement
     - Automatic orientation

4. `route.py`  
   - Class: `Router` (mixin)
   - Complex routing algorithms including:
     - Global routing
     - Detailed routing
     - Switchbox routing
     - Track management

5. `bboxes.py`
   - Functions for calculating component boundaries
   - Used for component placement
   - Handles:
     - Symbol bounding boxes
     - Label bounding boxes
     - Hierarchical sheet sizing

### Current Process Flow

1. Circuit Preprocessing (`gen_schematic.py:preprocess_circuit()`)
   ```python
   def preprocess_circuit(circuit, **options):
       # Initialize components
       # Set initial transformations
       # Calculate bounding boxes
   ```

2. Node Creation and Hierarchy (`node.py`)
   ```python
   class Node:
       def __init__(self, circuit, tool, filepath, top_name, title, flatness):
           # Create hierarchical structure
           # Organize components
           # Setup placement/routing framework
   ```

3. Component Placement (`place.py`)
   ```python
   def place(self, **options):
       # Group components
       # Place connected components
       # Place floating components
       # Place hierarchical blocks
   ```

4. Wire Routing (`route.py`)
   ```python
   def route(self, **options):
       # Create routing points
       # Generate routing tracks
       # Perform global routing
       # Perform detailed routing
   ```

5. KiCad Output Generation (`gen_schematic.py:node_to_eeschema()`)
   ```python
   def node_to_eeschema(node, sheet_tx=Tx()):
       # Generate hierarchical structure
       # Output component definitions
       # Output wire definitions
       # Generate sheet definitions
   ```

## Proposed Simplified Implementation

### Key Changes

1. Remove Complex Placement
   - Eliminate force-directed placement
   - Use simple grid-based placement
   - Remove component orientation optimization

2. Remove Wire Routing
   - Replace physical wires with net labels
   - Add net labels to component pins
   - Use KiCad's built-in ERC to validate connections

3. Focus on S-Expression Generation
   - Update for KiCad 8 format
   - Proper UUID handling
   - Modern property handling

### New Process Flow

1. Circuit Preprocessing
   ```python
   def preprocess_circuit(circuit):
       for part in circuit.parts:
           # Assign UUIDs
           # Calculate simple grid positions
           # Setup net labels
   ```

2. Hierarchical Sheet Creation
   ```python
   def create_hierarchical_structure(circuit):
       # Create top sheet
       # Create sub-sheets for hierarchical blocks
       # Setup sheet entries and exits (labels)
   ```

3. Component Placement
   ```python
   def place_components(sheet):
       # Use simple grid placement
       # Assign fixed positions
       # Add net labels to pins
   ```

4. KiCad Output Generation
   ```python
   def generate_kicad_output(circuit):
       # Generate file header
       # Output library symbols
       # Output components with labels
       # Output hierarchical sheets
       # Generate sheet entries
   ```

### S-Expression Format (KiCad 8)

1. File Structure
   ```scheme
   (kicad_sch
     (version 20231120)
     (generator "skidl")
     (uuid "...")
     (paper "A4")
     ;; Rest of schematic
   )
   ```

2. Component Definition
   ```scheme
   (symbol
     (lib_id "Device:R")
     (at 25.4 25.4 0)
     (unit 1)
     (uuid "...")
     (property "Reference" "R1" ...)
     (property "Value" "10k" ...)
     (pin "1" (uuid "..."))
     (pin "2" (uuid "..."))
   )
   ```

3. Net Labels
   ```scheme
   (text "Label"
     (at x y 0)
     (effects
       (font (size 1.27 1.27))
     )
     (uuid "...")
   )
   ```

4. Hierarchical Sheets
   ```scheme
   (sheet
     (at x y)
     (size w h)
     (uuid "...")
     (property "Sheet name" "...")
     (property "Sheet file" "...")
   )
   ```

### Implementation Example

```python
def generate_component(part):
    """Generate KiCad component definition."""
    return f"""
    (symbol
      (lib_id "{part.lib_name}:{part.name}")
      (at {part.x} {part.y} {part.rotation})
      (unit {part.unit})
      (uuid "{part.uuid}")
      {generate_properties(part)}
      {generate_pins(part)}
    )
    """

def generate_net_label(pin):
    """Generate net label for pin."""
    return f"""
    (text "{pin.net.name}"
      (at {pin.label_x} {pin.label_y} 0)
      (effects
        (font (size 1.27 1.27))
      )
      (uuid "{uuid.uuid4()}")
    )
    """
```

## Benefits of New Approach

1. Simplicity
   - Removes complex placement algorithms
   - Eliminates routing complexity
   - Easier to maintain and debug

2. Reliability
   - Fewer failure modes
   - More predictable output
   - Better compatibility with KiCad

3. Maintainability
   - Clearer code structure
   - Easier to update for new KiCad versions
   - Simpler testing

4. User Experience
   - Faster schematic generation
   - More predictable results
   - Easy manual adjustment if needed

## Next Steps

1. Implementation
   - Update file format handling for KiCad 8
   - Create simple grid placement system
   - Implement net label generation
   - Update hierarchical sheet handling

2. Testing
   - Create test suite for new format
   - Validate hierarchical designs
   - Test power distribution
   - Verify bus connections

3. Documentation
   - Update user documentation
   - Add examples for hierarchical designs
   - Document net labeling conventions
   - Provide migration guide

## File Format References

1. KiCad 8 Schematic Format: [Schematic_File_Format.md]
2. S-Expression Format: [s-expressions.md]
3. Example Files:
   - hierarchical_design.kicad_sch
   - linear_regulator.kicad_sch

## Questions/Additional Information Needed

1. Grid Placement
   - Preferred grid spacing
   - Component orientation rules
   - Sheet size calculations

2. Net Labels
   - Label placement rules
   - Power net handling
   - Bus label formatting

3. Hierarchy
   - Sheet size calculations
   - Sheet entry/exit labeling
   - Instance handling