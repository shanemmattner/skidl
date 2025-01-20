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
    def analyze_schematics_recursive(file_path, base_path, depth=0, debug=False):
        try:
            print(f"/n/r*****************  {'  ' * depth}Analyzing: {file_path}  *****************")
            schematic = Schematic().from_file(file_path)
            analyze_schematic(schematic, base_path, debug=debug)  # Your existing analysis function

            # Process all sub-sheets recursively
            if schematic.sheets:
                print(f"{'  ' * depth}=== Sub-sheets found ===")
                for sheet in schematic.sheets:
                    sub_file_path = os.path.join(base_path, sheet.fileName.value)
                    # Recursively analyze the sub-schematic
                    analyze_schematics_recursive(sub_file_path, base_path, depth + 1, debug=debug)
                    
        except Exception as e:
            print(f"{'  ' * depth}Error processing {file_path}: {str(e)}")

    # Usage
    base_path = os.path.dirname(file_path)
    analyze_schematics_recursive(file_path, base_path, debug=debug)


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python main.py <schematic_file_path> [-debug]")
        sys.exit(1)
        
    debug = len(sys.argv) == 3 and sys.argv[2] == "-debug"
    main(sys.argv[1], debug)
