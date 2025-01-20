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
        print(file_path)
        schematic = Schematic().from_file(file_path)
        # print(f"kiutils Schematic() object: {schematic}\n\r")

        analyze_schematic(schematic, base_path, debug=debug)

        print("\n=== Sheets Returned ===")
        for sheet in schematic.sheets:
            file_path_sub = os.path.join(base_path, sheet.fileName.value)
            schematic = Schematic().from_file(file_path_sub)
            analyze_schematic(schematic, sheet.fileName.value, debug=debug)
            # print(f"\nSheet: {sheet.sheetName.value}")
            # print(f"\tFile: {sheet.fileName.value}")
            # print(f"\tUUID: {sheet.uuid}")
    except Exception as e:
        print(f"Error processing schematic: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python main.py <schematic_file_path> [-debug]")
        sys.exit(1)
        
    debug = len(sys.argv) == 3 and sys.argv[2] == "-debug"
    main(sys.argv[1], debug)
