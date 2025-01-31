# KiCad Schematic Generation Refactoring Plan

## Overview

This document outlines the plan to refactor the KiCad schematic generation code in `src/skidl/tools/kicad8/sch_gen/` to leverage the existing library parsing and symbol handling logic in `src/skidl/tools/kicad8/lib.py`.

## Current Architecture

The current implementation has multiple components handling symbol parsing and flattening:

1. `kicad_library_parser.py`: Parses .kicad_sym files
2. `symbol_parser.py`: Another symbol parser implementation
3. `symbol_flatten.py`: Handles symbol inheritance
4. `symbol_definitions.py`: Defines data structures for symbols
5. `kicad_writer.py`: Writes KiCad schematic files
6. `hierarchy_manager.py`: Manages hierarchical sheets

## Target Architecture

The refactored implementation will:

1. Use `lib.py`'s robust parsing and flattening functionality:
   - `load_sch_lib()` for library parsing
   - `parse_lib_part()` for symbol parsing and flattening
   - Built-in inheritance handling via "extends"

2. Keep core schematic generation logic:
   - `gen_schematic_v8.py`
   - `hierarchy_manager.py`
   - Modified `kicad_writer.py`

## Detailed Changes

### Files to Remove

1. `kicad_library_parser.py`
   - Functionality replaced by `lib.py:load_sch_lib()`

2. `symbol_parser.py`
   - Functionality replaced by `lib.py:parse_lib_part()`

3. `symbol_flatten.py`
   - Inheritance handling replaced by `lib.py`'s implementation

4. `symbol_definitions.py`
   - Data structures replaced by `lib.py`'s Part class

### Files to Modify

1. `kicad_writer.py`
   
   Changes needed:
   - Remove custom symbol parsing logic
   - Update SchematicSymbolInstance to work with lib.py's Part objects:
     ```python
     class SchematicSymbolInstance:
         def __init__(self, part: Part, position: tuple = (0, 0)):
             self.lib_id = f"{part.lib.filename}:{part.name}"
             self.reference = part.ref
             self.value = part.value
             self.x = position[0]
             self.y = position[1]
             self.uuid = str(uuid.uuid4())
             self.footprint = part.footprint
     ```
   - Update symbol instance creation to use lib.py's parsing:
     ```python
     def create_symbol_instance(self, part: Part, position: tuple) -> SchematicSymbolInstance:
         return SchematicSymbolInstance(part, position)
     ```

2. `hierarchy_manager.py`

   Changes needed:
   - Update CircuitNode to work with lib.py's Part objects:
     ```python
     @dataclass
     class CircuitNode:
         instance_path: str
         sheet_name: str
         parent_path: Optional[str]
         children: List[str] = field(default_factory=list)
         parts: List[Part] = field(default_factory=list)
     ```
   - Update part placement logic to use Part object properties
   - Keep hierarchical sheet management logic unchanged

3. `gen_schematic_v8.py`

   Changes needed:
   - Update to use lib.py's Part objects throughout
   - Keep high-level schematic generation logic unchanged
   - Update debug printing to include Part object information

## Integration Steps

1. First Phase:
   - Remove deprecated files
   - Update data structures to use lib.py's Part class
   - Modify kicad_writer.py to use lib.py's parsing

2. Second Phase:
   - Update hierarchy_manager.py
   - Test hierarchical sheet generation
   - Verify symbol placement and connections

3. Final Phase:
   - Update gen_schematic_v8.py
   - Add comprehensive testing
   - Document new architecture

## Testing Strategy

1. Unit Tests:
   - Test Part object integration
   - Verify symbol parsing and flattening
   - Check hierarchical sheet generation

2. Integration Tests:
   - Test complete schematic generation
   - Verify hierarchical projects
   - Check symbol inheritance

3. Regression Tests:
   - Ensure existing functionality works
   - Verify backward compatibility
   - Check error handling

## Benefits

1. Code Reduction:
   - Eliminates duplicate parsing code
   - Removes redundant data structures
   - Simplifies maintenance

2. Improved Functionality:
   - More robust symbol parsing
   - Better inheritance handling
   - Consistent data structures

3. Better Maintainability:
   - Single source of truth for parsing
   - Clearer architecture
   - Better code organization

## Risks and Mitigation

1. Risks:
   - Breaking changes in hierarchical sheet handling
   - Symbol placement differences
   - Performance impact

2. Mitigation:
   - Comprehensive testing suite
   - Gradual rollout of changes
   - Performance benchmarking

## Timeline

1. Week 1:
   - Remove deprecated files
   - Update data structures

2. Week 2:
   - Modify kicad_writer.py
   - Update hierarchy_manager.py

3. Week 3:
   - Testing and debugging
   - Documentation updates

## Future Improvements

1. Performance Optimization:
   - Cache parsed symbols
   - Optimize memory usage

2. Feature Additions:
   - Enhanced symbol inheritance
   - Better error reporting
   - Extended debugging capabilities