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
3. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
```
4. Install SKiDL:
```bash
pip install skidl
```

## Usage

Run the converter on your KiCad schematic:

```bash
python3 main.py <path_to_kicad_sch_file>
```

For example:
```bash
python3 main.py ../example_kicad_project/example_kicad_project.kicad_sch

Found 2 sheets:
- resistor_divider: resistor_divider.kicad_sch
- power2: power2.kicad_sch

Creating output directory: .../kicad_to_skidl/generated_subcircuits

Processing sheet: resistor_divider

Components found:
- R1: Device:R (Resistor_SMD:R_0603_1608Metric)
- R2: Device:R (Resistor_SMD:R_0603_1608Metric)

Hierarchical labels found:
- Label(name='R1_2-R2_1', x=121.92, y=72.39)
Generated SKiDL subcircuit in '.../kicad_to_skidl/generated_subcircuits/resistor_divider_subcircuit.py'

Processing sheet: power2

Components found:
- U1: Regulator_Linear:NCP1117-3.3_SOT223 (Package_TO_SOT_SMD:SOT-223-3_TabPin2)
- C2: Device:C (Capacitor_SMD:C_0603_1608Metric)
- C1: Device:C (Capacitor_SMD:C_0603_1608Metric)
Generated SKiDL subcircuit in '.../kicad_to_skidl/generated_subcircuits/power2_subcircuit.py'

Generated main circuit in '.../kicad_to_skidl/generated_subcircuits/main_circuit.py'

Successfully processed schematic
```

After generation, you can run the generated main circuit to create a netlist:

```bash
python3 generated_subcircuits/main_circuit.py
INFO: No errors or warnings found while generating netlist.
```

The tool will:
1. Parse the main schematic file
2. Find all hierarchical sheets
3. Generate SKiDL subcircuits for each sheet
4. Create a main circuit file that connects everything together

Output files will be created in a `generated_subcircuits` directory:
- `<sheet_name>_subcircuit.py` for each sheet
- `main_circuit.py` that imports and connects all subcircuits

## Project Structure

```
kicad_to_skidl/
├── main.py                 # Main script
├── config.py              # Configuration settings
├── schematic_processor.py # Core processing logic
├── README.md              # This file
├── parsers/              # Parser modules
│   ├── __init__.py
│   ├── base_parser.py     # Base parsing functionality
│   ├── component_parser.py # Parses components
│   └── sheet_parser.py    # Parses sheet structure
├── generators/           # Code generation modules
│   ├── __init__.py
│   └── base_generator.py  # Base generation functionality
└── generated_subcircuits/ # Output directory
    ├── main_circuit.py    # Generated main circuit
    └── *_subcircuit.py   # Generated subcircuits
```

## Supported Components

- Resistors (Device:R)
- Capacitors (Device:C)
- Voltage Regulators (e.g., NCP1117-3.3_SOT223)
- Power symbols
- Hierarchical labels

## Notes

- Component footprints are preserved from KiCad (e.g., R_0603_1608Metric)
- Power nets (GND, VCC) are automatically handled
- Hierarchical labels are converted to SKiDL nets
- Special handling for voltage regulators with proper pin connections
- Generated code includes ERC (Electrical Rules Check) verification


## Other
- List pins on part with command:
```
shanemattner@Shanes-MacBook-Pro skidl % python3 -c "from skidl import * ; part = Part('MCU_ST_STM32G4', 'STM32G431C6Ux'); print('Available pins:
', [pin.name for pin in part.pins])"
Available pins: ['VBAT', 'PA2', 'PA3', 'PA4', 'PA5', 'PA6', 'PA7', 'PC4', 'PB0', 'PB1', 'PB2', 'PC13', 'VREF+', 'VDDA', 'PB10', 'VDD', 'PB11', 'PB12', 'PB13', 'PB14', 'PB15', 'PC6', 'PC14', 'PA8', 'PA9', 'PA10', 'PA11', 'PA12', 'VDD', 'PA13', 'PA14', 'PA15', 'PC10', 'PC15', 'PC11', 'PB3', 'PB4', 'PB5', 'PB6', 'PB7', 'PB8', 'PB9', 'VDD', 'VSS', 'PF0', 'PF1', 'PG10', 'PA0', 'PA1']
```