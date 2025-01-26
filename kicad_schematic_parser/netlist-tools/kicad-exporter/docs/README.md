# KiCad Netlist Exporter

## Requirements
- Python 3.8+
- KiCad 8.0+ (or set KICAD8_SYMBOL_DIR environment variable)

## Installation
```bash
chmod +x src/kicad_netlist_export.py
```

## Usage
```bash
./src/kicad_netlist_export.py path/to/project.kicad_sch [-o output.net]
```

## Environment Variables
- `KICAD8_SYMBOL_DIR`: Override default KiCad installation path (e.g. /path/to/kicad/share/kicad/symbols)

## Examples
```bash
# Basic usage with default output name
./src/kicad_netlist_export.py example_project.kicad_sch

# Custom output path
./src/kicad_netlist_export.py example_project.kicad_sch -o custom.net

# Use environment variable override
KICAD8_SYMBOL_DIR="/custom/kicad/path" ./src/kicad_netlist_export.py project.kicad_sch
```

## Error Handling
Common error scenarios include:
- Missing KiCad installation
- Invalid schematic file path
- Write permissions issues
- Invalid KiCad version

Errors will display clear messages with troubleshooting suggestions.

## Roadmap
- Netlist validation tools
- SPICE simulation integration
- Cross-platform support enhancements
- Batch processing capabilities
