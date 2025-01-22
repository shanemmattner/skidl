#!/bin/bash

# Generate reference outputs for all test schematics
SCHEMATICS=("resistor_divider" "power2" "stm32")
OUTPUT_DIR="reference_outputs"

mkdir -p $OUTPUT_DIR

for schematic in "${SCHEMATICS[@]}"; do
    python3 src/main.py --mode kicad2text \
        "src/kicad_hierarchy_parser/tests/net_parsing_tests/${schematic}.kicad_sch" \
        > "$OUTPUT_DIR/${schematic}_output.txt"
done

echo "Generated reference outputs in $OUTPUT_DIR/"