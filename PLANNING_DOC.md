Let me create a comprehensive planning document for the netlist-to-skidl converter.



# KiCad Netlist to SKiDL Converter Design Document

## Overview
This document details the design and implementation plan for converting KiCad netlists (.net files) into hierarchical SKiDL Python files. The converter will enable seamless transition between KiCad schematics and SKiDL code while preserving hierarchy and component properties.

## Design Goals
1. Convert KiCad netlists into readable, maintainable SKiDL Python code
2. Preserve hierarchical sheet structure from KiCad
3. Maintain exact component references and net names
4. Support both flat and hierarchical designs
5. Enable round-trip editing between KiCad and SKiDL

## File Structure

### Input Format
KiCad netlist (.net) file containing:
- Sheet definitions with hierarchy
- Component definitions with properties
- Net connections
- Library references

### Output Structure
Generated Python files matching KiCad hierarchy:
```
project/
├── example_kicad_project.py  (root sheet)
├── esp32s3mini1.py
│   └── resistor_divider1.py
├── power2.py
└── usb.py
```

## Implementation Approach

### 1. Sheet Parsing
First pass through netlist to identify all sheets and their hierarchy.

Example sheet entry from netlist:
```xml
(sheet (number "4") (name "/esp32s3mini1/resistor_divider1/") 
  (tstamps "/e6f5f316-cb92-4d26-9a5c-0bb6c841d4b0/0f8673e0-e78a-49db-bb03-1ef92ea13213/"))
```

Generated Python structure:
```python
# resistor_divider1.py
@subcircuit
def resistor_divider1(vin, vout, gnd):
    # Components
    c10 = Part("Device", "C", value="100nF", 
               footprint="Capacitor_SMD:C_0603_1608Metric")
    r9 = Part("Device", "R", value="2k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r10 = Part("Device", "R", value="1k",
               footprint="Resistor_SMD:R_0603_1608Metric")
    
    # Connections
    vin += r9[1]
    vout += c10[1], r10[1], r9[2]
    gnd += c10[2], r10[2]
```

### 2. Component Parsing
For each sheet, identify and parse its components:
- Preserve exact reference designators
- Include only necessary properties (value, footprint)
- Omit unconnected pins
- Group components by sheet using sheetpath property

Example component from netlist:
```xml
(comp (ref "C10")
  (value "100nF")
  (footprint "Capacitor_SMD:C_0603_1608Metric")
  (property (name "Sheetname") (value "resistor_divider1")))
```

### 3. Net Handling
Process nets in order:
1. Power nets (+3V3, +5V)
2. Sheet-level nets
3. Hierarchical interconnects

Example net handling:
```python
# example_kicad_project.py (root)
def example_kicad_project():
    # Create high-level nets
    vcc3v3 = Net("+3V3")
    vcc5v0 = Net("+5V")
    gnd = Net("GND")
    
    # Call subsheets with required nets
    esp32s3mini1(vcc3v3, vcc5v0, gnd)
    power2(vcc3v3, vcc5v0, gnd)
    usb(vcc5v0, gnd)
```

### 4. Hierarchy Construction
For nested sheets:
1. Import child modules into parent modules
2. Pass required nets through function parameters
3. Maintain exact net names from KiCad

Example hierarchy:
```python
# esp32s3mini1.py
from .resistor_divider1 import resistor_divider1

@subcircuit
def esp32s3mini1(vcc3v3, gnd):
    # Local components
    u3 = Part("RF_Module", "ESP32-S3-MINI-1", ...)
    c1 = Part("Device", "C", value="10uF", ...)
    
    # Local nets
    hw_ver = Net("/esp32s3mini1/HW_VER")
    
    # Call nested subcircuit
    resistor_divider1(vcc3v3, hw_ver, gnd)
```

## Technical Details

### Parser
- Use kinparse for initial XML parsing
- Parse in order: sheets -> components -> nets
- Throw error on malformed netlist at point of failure

### Component Handling
- Preserve exact KiCad reference designators
- Include only value and footprint properties
- Omit unconnected pins entirely

### Net Names
- Preserve exact KiCad net names including:
  - Power nets ("+3V3", "+5V")
  - Local nets ("Net-(P1-CC)")
  - Hierarchical nets ("/esp32s3mini1/EN")

### Pin Handling
- Support both numeric and named pins (e.g., "A1", "B5")
- Use strings for all pin references in generated code
- Example: `part["A1"] += net`

## Test Cases

1. Flat design with single sheet
2. Two-level hierarchy
3. Nested hierarchy (3+ levels)
4. Complex components (ESP32 with many pins)
5. Mixed pin types (numeric and named)
6. Cross-sheet power networks
7. Local-only nets
8. Multiple instances of same subcircuit

## Future Considerations

1. Component templates for repeated parts
2. Integration with KiCad Python API
3. Back-conversion from SKiDL to netlist
4. Support for additional netlist formats
5. Library management
6. Error recovery and partial conversion

## Example Usage

```python
# Convert netlist to SKiDL 
from netlist_to_skidl import convert_netlist
convert_netlist("project.net", "output_dir")

# Generated files can be used as:
from example_kicad_project import example_kicad_project
example_kicad_project()
generate_netlist()
```

This document provides the foundation for implementing the KiCad netlist to SKiDL converter while maintaining all critical design aspects and hierarchical relationships.