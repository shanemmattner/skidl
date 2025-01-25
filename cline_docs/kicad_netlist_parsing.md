# KiCad Netlist to SKiDL Conversion System

## Core Components
**Conversion Engine:** `src/skidl/netlist_to_skidl.py`
- HierarchicalConverter class handles sheet hierarchy
- legalize_name() critical for Python identifier compliance

## Key Functions
### legalize_name(name: str)
Handles special characters conversion:
- Leading numbers ➔ prefixed with "_"
- "+" in net names ➔ converted to "_p" (e.g., D+ ➔ D_p)
- "/" in sheet paths ➔ converted to nested modules
- Spaces/special chars ➔ replaced with underscores

## Validation Process
1. Generate files:
```bash
python3 -c "from src.skidl.netlist_to_skidl import netlist_to_skidl; netlist_to_skidl('example_kicad_project.net', 'example_kicad_project_test')"
```

2. Test output:
```bash
python3 example_kicad_project_test/main.py
```

## Current State
- Successfully converts complex hierarchical designs
- Handles differential pair nets (D+/D- ➔ D_p/D_n)
- Generates import-safe module names
- Validated with ESP32-S3-Mini and USB-C designs

## Limitations
- Circular imports between sheets not fully resolved
  - Requires manual intervention for complex hierarchy loops
