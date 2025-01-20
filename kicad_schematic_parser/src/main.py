#!/usr/bin/env python3
import sys
import os
from kiutils.schematic import Schematic
from skidl_kicad_parser import analyze_schematic

def main(file_path):
    """
    Main entry point for the KiCad schematic parser
    """
    # Load the schematic
    base_path = os.path.dirname(file_path)
    try:
        schematic = Schematic().from_file(file_path)
        analyze_schematic(schematic, base_path)
    except Exception as e:
        print(f"Error processing schematic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <schematic_file_path>")
        sys.exit(1)
    main(sys.argv[1])
