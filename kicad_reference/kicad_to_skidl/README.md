# KiCad to SKiDL Converter

This tool converts KiCad hierarchical schematics into SKiDL Python code. It parses KiCad schematic sheets and generates equivalent SKiDL subcircuits that can be used to programmatically create the same circuit.

## Features

- Parses KiCad hierarchical sheets
- Extracts components, footprints, and connections
- Generates SKiDL subcircuits for each sheet
- Creates a main circuit file that connects all subcircuits
- Handles power nets and hierarchical labels
- Supports special components like voltage regulators

## Installation

1. Clone this repository
2. Ensure you have Python 3.x installed
3. Install SKiDL:
```bash
pip install skidl
```

## Usage

Run the converter on your KiCad schematic:

```bash
python main.py path/to/your/schematic.kicad_sch
```

The tool will:
1. Parse the main schematic file
2. Find all hierarchical sheets
3. Generate SKiDL subcircuits for each sheet
4. Create a main circuit file that connects everything together

Output files will be created in a `generated_subcircuits` directory:
- `<sheet_name>_subcircuit.py` for each sheet
- `main_circuit.py` that imports and connects all subcircuits

## Example

For a schematic with two sheets (resistor_divider and power2):

```python
# Generated main_circuit.py
from skidl import *

# Define power nets that will be shared across subcircuits
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

from resistor_divider_subcircuit import resistor_divider
from power2_subcircuit import power2

# Instantiate the power nets
vcc_5v = Net('+5V')
vcc_5v.drive = POWER

# Instantiate the subcircuits
net_0 = resistor_divider(vcc_5v)
final_net = power2(net_0)

# Generate netlist
generate_netlist()
```

## Project Structure

```
kicad_to_skidl/
├── main.py              # Main script
├── README.md           # This file
└── parsers/            # Parser modules
    ├── sheet_parser.py    # Parses sheet names and files
    └── component_parser.py # Parses components and generates SKiDL code
```

## Supported Components

- Resistors
- Capacitors
- Voltage Regulators
- Power symbols
- Hierarchical labels

## Notes

- Component values are currently hardcoded (1K for resistors, 10uF for capacitors)
- Power nets (GND, VCC) are automatically handled
- Hierarchical labels are converted to SKiDL nets
- Special handling for voltage regulators with proper pin connections
