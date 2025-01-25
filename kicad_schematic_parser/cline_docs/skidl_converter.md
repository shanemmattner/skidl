# SKiDL Converter Implementation

## Core Capabilities
- ✅ Schematic-to-SKiDL conversion workflow
- ✅ Component reference normalization (lowercase)
- ✅ Automatic power net detection (GND handling)
- ✅ Hierarchical I/O port classification
- ✅ Deterministic code output ordering

## Test Validation
```python
def test_resistor_divider_skidl_generation():
    # ARRANGE
    test_input = '''=== Components ===
    Component: Device/R
    Properties:
        Reference: R9
        Value: 2k
    === Netlist ===
    NET_A:
    R9-1
    NET_B: 
    R9-2
    '''
    
    # ACT
    result = sheet_to_skidl("divider", test_input)
    
    # ASSERT
    assert "r9[1] += vin" in result
    assert "r9[2] += vout" in result
    assert "GND" in result
```

## CLI Implementation
```python
@click.command()
@click.argument('input_file')
@click.argument('output_file')
def convert_schematic(input_file, output_file):
    """Convert KiCad schematic text to SKiDL"""
    with open(input_file) as f:
        skidl_code = sheet_to_skidl("Circuit", f.read())
    with open(output_file, 'w') as f:
        f.write(skidl_code)
```

## Memory Bank Updates
- Unit tests validate net connectivity patterns
- Component references normalized to lowercase
- GND handling hardcoded as power net
- Hierarchical ports use pin count heuristic
- Deterministic output via sorted collections
