# Net Parsing Improvement Documentation

## Problem Analysis
### Initial Issue
- Netlist generation using MERGED_NET_x names instead of hierarchical labels
- Misidentification of power vs hierarchical labels
- Incomplete connectivity analysis across sheet boundaries

### Key Findings
1. Label priority inversion in net naming (power > hierarchical)
2. Hierarchical sheet pin connections not properly traced
3. Missing label propagation through multi-sheet connections

## Test Strategy
### Principles Applied
- **KISS**: Minimal test cases covering core scenarios
- **YAGNI**: Focused only on current schematic examples
- **SOLID**:
  - Single responsibility for each test
  - Open/closed principle for test extensibility

### Test Matrix
| Schematic | Test Coverage |
|-----------|---------------|
| resistor_divider | Basic net formation, label priority |
| power2 | Multi-rail power distribution |
| stm32 | Hierarchical sheet connections |

## Implementation Details
### Core Changes
1. Net naming priority:
   ```python
   Sheet pins > Hierarchical labels > Power labels > Local labels > Generated ID
   ```
2. Enhanced connection tracing:
   - Recursive wire/pin connectivity analysis
   - Cross-sheet label propagation

### Test Infrastructure
```bash
src/kicad_hierarchy_parser/tests/net_parsing_tests/
├── generate_reference_outputs.sh
├── test_net_parsing.py
├── README.md
└── reference_outputs/
```

## Validation Process
```bash
# Generate reference outputs
./generate_reference_outputs.sh

# Run tests (from project root)
python3 -m pytest src/kicad_hierarchy_parser/tests/net_parsing_tests/ -v

# Update tests after changes
pytest --update-snapshots
```

## Maintenance Guide
1. Adding New Tests:
   - Place schematic in test directory
   - Add test function in test_net_parsing.py
   - Generate reference output

2. Key Maintenance Points:
   - Keep schematic paths relative
   - Maintain label type separation
   - Update reference outputs after parser changes