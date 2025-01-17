# SKiDL Schematic Generation - LLM Prompt Strategy

## Overall Approach

Break down the implementation into distinct phases with clear inputs, outputs, and testing criteria. Each phase should have its own focused prompt that:
1. Provides relevant context
2. States clear objectives
3. Requests specific outputs
4. Includes testing criteria

## Phase Structure

### Phase 1: File Format Analysis
**Purpose**: Create mapping between current and new format

**Prompt Template**:
```
Context:
- KiCad 8 schematic examples:
  - hierarchical_design.kicad_sch
  - linear_regulator.kicad_sch
  - 1_resistor.kicad_sch
- KiCad 8 symbol libraries (key components):
  - Device.kicad_sym (basic components like R, C, L)
  - power.kicad_sym (power symbols)
  - Connector_Generic.kicad_sym (connectors)
- Here is current SKiDL output format: [current_output.txt]
- Here is format documentation: [format_docs.md]

Task: Create a detailed mapping showing:
1. Required format changes
2. New fields/properties needed
3. UUID handling requirements

Please analyze these specific sections:
1. File header
2. Component definitions
3. Net connections

Output Format:
1. Section-by-section comparison
2. Required changes list
3. Implementation recommendations
```

**Success Criteria**:
- Clear mapping between formats
- All required fields identified
- UUID requirements documented

### Phase 2: Simple Component Placement
**Purpose**: Implement basic grid-based component placement

**Prompt Template**:
```
Context:
- Here is current placement code: [place.py]
- Here is desired grid-based approach: [description]

Task: Create simplified placement logic that:
1. Places components on a grid
2. Handles hierarchical sheets
3. Avoids overlaps

Please provide:
1. Updated class structure
2. Core placement algorithm
3. Example outputs

Testing Approach:
1. Test with simple circuit
2. Verify grid alignment
3. Check hierarchical handling
```

**Success Criteria**:
- Components placed without overlap
- Grid alignment maintained
- Hierarchy preserved

### Phase 3: Net Label Generation
**Purpose**: Replace wire routing with net labels

**Prompt Template**:
```
Context:
- Current routing approach: [route.py]
- KiCad 8 label format: [format_doc.md]
- Example circuit: [example.py]

Task: Create net label generation that:
1. Identifies connected pins
2. Creates appropriate labels
3. Places labels correctly

Please provide:
1. Label generation algorithm
2. Label placement strategy
3. Power net handling approach

Testing:
1. Simple net connections
2. Bus connections
3. Power distribution
```

**Success Criteria**:
- Labels correctly generated
- Proper placement
- Power nets handled

### Phase 4: Hierarchical Support
**Purpose**: Implement hierarchical sheet handling

**Prompt Template**:
```
Context:
- Current hierarchy code: [node.py]
- KiCad 8 hierarchy example: [hier_example.kicad_sch]
- Hierarchy requirements: [list]

Task: Update hierarchical handling to:
1. Create proper sheet structure
2. Handle sheet entries/exits
3. Manage sheet instances

Please provide:
1. Sheet creation logic
2. Entry/exit handling
3. Instance management

Testing:
1. Basic hierarchy
2. Multiple instances
3. Sheet connections
```

**Success Criteria**:
- Proper sheet structure
- Correct entry/exit labels
- Instance handling works

## Iteration Strategy

1. **Start Small**
   - Begin with simplest possible circuit
   - Add complexity gradually
   - Test each step thoroughly

2. **Keep Context Focused**
   - Provide only relevant code/docs
   - Clear scope for each prompt
   - Specific success criteria

3. **Progressive Enhancement**
   - Start with basic functionality
   - Add features incrementally
   - Validate each addition

## Sample Initial Prompt

Here's a concrete example for starting Phase 1:

```
I'm updating SKiDL's schematic generation to work with KiCad 8. I'd like to analyze the file format changes needed.

Context:
1. Current SKiDL output: [attached current_output.txt]
2. KiCad 8 format: [attached kicad8_example.kicad_sch]
3. Format documentation: [attached format_docs.md]

Please help me create a detailed mapping of the file format changes needed. Focus on:
1. File header structure
2. Basic component definition
3. Required UUID handling

Output needed:
1. Side-by-side comparison of old vs new format
2. List of required changes
3. Specific examples of the new format

Please keep the analysis focused on just these areas for now. We'll handle other aspects in subsequent steps.
```

## Tips for Using These Prompts

1. **Provide Clear Context**
   - Include relevant code snippets
   - Reference specific files
   - State current status

2. **Set Clear Boundaries**
   - Define specific scope
   - State explicit requirements
   - List expected outputs

3. **Request Iterative Feedback**
   - Ask for implementation suggestions
   - Request potential issues
   - Seek testing approaches

4. **Progressive Development**
   - Start with core functionality
   - Add features gradually
   - Test at each step

## Test-Driven Approach

For each phase:

1. **Create Test Cases**
   - Simple circuit
   - Expected output
   - Edge cases

2. **Define Success Criteria**
   - Format correctness
   - Functional requirements
   - Error handling

3. **Validate Results**
   - KiCad compatibility
   - Circuit correctness
   - Code quality

## Next Steps

1. Start with Phase 1 prompt
2. Analyze results
3. Refine prompt based on feedback
4. Proceed to next phase

This structured approach will help keep the development focused and manageable while ensuring we maintain quality and correctness throughout the process.