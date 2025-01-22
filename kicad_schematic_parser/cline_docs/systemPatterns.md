## Net Parsing Architecture

### Parsing Strategy
- **Hierarchical Approach**: Multi-level net tracing
- **Priority-Based Naming**: Strict label resolution hierarchy
- **Recursive Connectivity**: Comprehensive net connection tracking

### Key Design Principles
1. **KISS (Keep It Simple, Stupid)**
   - Minimal test cases
   - Focused parsing logic
   
2. **YAGNI (You Aren't Gonna Need It)**
   - Only implement currently required functionality
   - Avoid over-engineering

3. **SOLID Principles**
   - Single Responsibility: Separate concerns in parsing
   - Open/Closed: Extensible parsing framework
   - Dependency Inversion: Loose coupling between parsing components

### Net Naming Priority
```
1. Sheet Pins
2. Hierarchical Labels
3. Power Labels
4. Local Labels
5. Generated ID
```

### Connectivity Analysis
- Recursive wire/pin traversal
- Cross-sheet label propagation
- Comprehensive net formation algorithm

### Test Infrastructure
- Location: `src/kicad_hierarchy_parser/tests/net_parsing_tests/`
- Principles:
  * Focused test scenarios
  * Reproducible test cases
  * Snapshot-based validation
