#!/usr/bin/env python3
import sys
import os
from kiutils.schematic import Schematic
from skidl_kicad_parser import analyze_schematic

def main(file_path, debug=False):
    """
    Main entry point for the KiCad schematic parser
    
    Args:
        file_path: Path to the KiCad schematic file
        debug: Enable debug output
    """
    # Load the schematic
    base_path = os.path.dirname(file_path)
    try:
        schematic = Schematic().from_file(file_path)
        # print(schematic)
        analyze_schematic(schematic, base_path, debug=debug)
    except Exception as e:
        print(f"Error processing schematic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python main.py <schematic_file_path> [-debug]")
        sys.exit(1)
        
    debug = len(sys.argv) == 3 and sys.argv[2] == "-debug"
    main(sys.argv[1], debug)
