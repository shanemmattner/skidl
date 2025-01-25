# KiCad Netlist to SKiDL Converter Design Document

## Overview
This document details the design and implementation plan for converting KiCad netlists (.net files) into SKiDL Python files. The converter creates a direct 1:1 mapping between KiCad schematics and SKiDL code, maintaining exact hierarchy and naming to enable users to easily navigate between KiCad and SKiDL representations.

## Core Principles
1. Maintain exact 1:1 correspondence with KiCad schematic
2. Preserve KiCad net names while ensuring valid Python syntax
3. No special handling of power nets or global nets
4. No automatic optimization or encapsulation
5. Preserve exact sheet hierarchy as defined in KiCad
6. Generate code that is easy to follow from KiCad to SKiDL and back

## Design Goals
1. Convert KiCad netlists into readable, maintainable SKiDL Python code
2. Preserve hierarchical sheet structure exactly as in KiCad
3. Maintain exact component references and net names (converted to valid Python)
4. Support both flat and hierarchical designs
5. Match KiCad structure precisely in generated code

## Input Format
KiCad netlist (.net) file containing:
- Sheet definitions with hierarchy
- Component definitions with properties
- Net connections
- Library references

### Example Input Elements
```xml
# Sheet Definition
(sheet (number "4") (name "/esp32s3mini1/resistor_divider1/") 
  (tstamps "/e6f5f316-cb92-4d26-9a5c-0bb6c841d4b0/0f8673e0-e78a-49db-bb03-1ef92ea13213/"))

# Component Definition
(comp (ref "C10")
  (value "100nF")
  (footprint "Capacitor_SMD:C_0603_1608Metric")
  (property (name "Sheetname") (value "resistor_divider1")))
```

## Implementation Details

### 1. Parser (using kinparse)
- Parse sheets, components, and nets in order
- Maintain exact hierarchical structure
- Track sheet membership of components
- Preserve all net connections exactly as defined
- Throw error on malformed netlist at point of failure

### 2. Component Handling
- Preserve exact KiCad reference designators
- Include all properties (value, footprint)
- Maintain component sheet assignments
- Keep pin connections exactly as in KiCad

### 3. Net Names and Connections
- Convert KiCad net names to valid Python while preserving meaning:
  ```
  KiCad Name          Python Variable Name
  "/esp32s3mini1/EN" → esp32s3mini1_en
  "+3V3"            → net_3v3
  "Net-(P1-CC)"     → net_p1_cc
  ```
- Maintain exact connection topology
- No special handling of power or global nets
- All nets must be explicitly passed through hierarchy

### 4. Pin References
- Support both numeric and named pins (e.g., "A1", "B5")
- Use strings for all pin references
- Example: `part["A1"] += net`

## Test Cases
1. Flat design with single sheet
   - Verify component creation
   - Verify net connections
   - Verify pin references

2. Two-level hierarchy
   - Verify sheet structure
   - Verify net passing
   - Verify component grouping

3. Nested hierarchy (3+ levels)
   - Verify nested sheet imports
   - Verify net propagation
   - Verify naming consistency

4. Complex components (ESP32)
   - Verify multi-pin components
   - Verify named pins
   - Verify unconnected pins

5. Mixed pin types
   - Verify numeric pins
   - Verify alphanumeric pins
   - Verify special character pins

6. Power networks
   - Verify power net naming
   - Verify explicit passing
   - No implicit connections

7. Local nets
   - Verify sheet-local nets
   - Verify hierarchical nets
   - Verify net naming conversion

## Example Outputs

### Flat Circuit
```python
@subcircuit
def resistor_divider(vin, vout, gnd):
    # Components
    c10 = Part("Device", "C", value="100nF", 
               footprint="Capacitor_SMD:C_0603_1608Metric")
    r9 = Part("Device", "R", value="2k", 
              footprint="Resistor_SMD:R_0603_1608Metric")
    r10 = Part("Device", "R", value="1k",
               footprint="Resistor_SMD:R_0603_1608Metric")
    
    # Connections exactly as in KiCad
    vin += r9["1"]
    vout += c10["1"], r10["1"], r9["2"]
    gnd += c10["2"], r10["2"]
```

### Hierarchical Circuit
```python
@subcircuit
def esp32s3mini1(net_3v3, gnd, net_en):
    # Components in this sheet
    u3 = Part("RF_Module", "ESP32-S3-MINI-1")
    c1 = Part("Device", "C", value="10uF")
    
    # Local nets
    hw_ver = Net("esp32s3mini1_hw_ver")
    
    # Connections exactly as in KiCad
    net_3v3 += c1["1"], u3["3"]
    gnd += c1["2"], u3["1"]
    
    # Call subcircuit with explicit nets
    resistor_divider1(net_3v3, hw_ver, gnd)
```

## Usage
```python
# Convert netlist to SKiDL 
netlist_to_skidl("project.net", "output_dir")
```

This implementation focuses on creating a predictable, exact mapping between KiCad and SKiDL representations, making it easy for users to work with either format.