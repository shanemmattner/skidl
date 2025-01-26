# KiCad Netlist to SKiDL Converter Design Document

## Current Issues and Bugs

### 1. Component Reference Mismatch
- **Bug**: In esp32s3mini1.py, components are defined with sheet prefixes (esp32s3mini1_C1) but referenced without prefixes (C1)
- **Error**: NameError: name 'C1' is not defined
- **Example**:
  ```python
  # Defined as:
  esp32s3mini1_C1 = Part('Device', 'C', value='10uF')
  
  # But referenced as:
  _3V3 += C1['1']  # Should be esp32s3mini1_C1['1']
  ```

### 2. Net Name Inconsistencies
- **Bug**: Net names are being inconsistently converted between files
- **Example**:
  - In main.py: `_D_ = Net('_D_')`
  - In esp32s3mini1.py: `_D_ += U3['24']`
  - In USB.py: `D_n = Net('D_n')`
  
### 3. Hierarchical Net Passing
- **Bug**: Nets aren't being properly passed through hierarchy
- **Example**:
  - Main defines `_D_` but USB.py expects `D_n` and `D_p`
  - No clear mapping between hierarchical net names

### 4. Duplicate GND Nets
- **Bug**: Multiple GND nets being created unnecessarily
- **Example**:
  ```python
  # In main.py
  gnd = Net('GND')
  GND = Net('GND')  # Duplicate
  ```

### 5. Missing Net Connections
- **Bug**: Some nets from KiCad aren't appearing in SKiDL output
- **Example**:
  - KiCad net "/esp32s3mini1/EN" missing from output
  - KiCad net "Net-(P1-CC)" converted to "Net_n_P1_nCC_" but not properly connected

## Desired Behavior

1. **Component References**:
   - Use consistent component references matching KiCad refdes
   - Example: C1 should be C1 everywhere, not esp32s3mini1_C1

2. **Net Naming**:
   - Consistent net name conversion across all files
   - Preserve KiCad net hierarchy in names
   - Example: "/esp32s3mini1/EN" → esp32s3mini1_en

3. **Hierarchy Handling**:
   - Properly pass nets through hierarchy
   - Maintain exact KiCad net connections
   - Example: USB D+/D- should match ESP32 connections exactly

4. **Power Nets**:
   - Single GND net definition
   - Proper power net handling (+3V3, +5V)
   - No duplicate net definitions

## Proposed Changes

### 1. Component Reference Fix
```python
# Current
esp32s3mini1_C1 = Part(...)

# Proposed
C1 = Part(...)  # Use exact KiCad refdes
```

### 2. Net Name Standardization
```python
# Current
_D_ = Net('_D_')

# Proposed
d_n = Net('d_n')  # Consistent lowercase with underscores
d_p = Net('d_p')
```

### 3. Hierarchy Net Passing
```python
# Current
def esp32s3mini1(GND, _3V3, ...)

# Proposed
def esp32s3mini1(gnd, net_3v3, en, ...)  # Explicit net names
```

### 4. Single GND Net
```python
# Current
gnd = Net('GND')
GND = Net('GND')

# Proposed
gnd = Net('GND')  # Single definition
```

### 5. Complete Net Mapping
```python
# Current
Missing nets like esp32s3mini1_en

# Proposed
# Add all nets from KiCad netlist
esp32s3mini1_en = Net('esp32s3mini1_en')
net_p1_cc = Net('net_p1_cc')
```

## Implementation Plan

1. Update net name conversion to be consistent:
   - Convert all names to lowercase
   - Replace special chars with underscores
   - Preserve hierarchy in names

2. Fix component references:
   - Use exact KiCad refdes
   - Remove sheet prefixes

3. Implement proper net passing:
   - Map all nets through hierarchy
   - Maintain exact KiCad connections

4. Add validation:
   - Verify all KiCad nets appear in output
   - Check for duplicate nets
   - Validate net connections match

5. Update test cases:
   - Add tests for net name conversion
   - Add hierarchy passing tests
   - Add component reference tests

## Example Fixed Output

### esp32s3mini1.py
```python
@subcircuit
def esp32s3mini1(gnd, net_3v3, net_en, net_hw_ver, ...):
    # Components
    C1 = Part('Device', 'C', value='10uF')
    J1 = Part('Connector_Generic', 'Conn_02x03_Odd_Even')
    U3 = Part('RF_Module', 'ESP32-S3-MINI-1')

    # Connections
    net_3v3 += C1['1'], J1['2'], U3['3']
    net_en += J1['1'], U3['45']
    net_hw_ver += U3['5']
    gnd += C1['2'], J1['4'], U3['1']
```

### main.py
```python
def main():
    # Single GND net
    gnd = Net('GND')
    
    # Consistent net names
    net_3v3 = Net('net_3v3')
    net_5v = Net('net_5v')
    net_en = Net('net_en')
    net_hw_ver = Net('net_hw_ver')
    
    # Call subcircuits
    esp32s3mini1(gnd, net_3v3, net_en, net_hw_ver, ...)
```

This update documents the current issues and provides a clear path forward for fixing the netlist conversion process.
