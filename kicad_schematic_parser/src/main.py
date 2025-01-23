#!/usr/bin/env python3
import sys
import os
import argparse
from kiutils.schematic import Schematic
from kicad_hierarchy_parser import analyze_schematic
from skidl_generator.component_parser.component_parser import parse_component_name, parse_component_properties, parse_component_block, generate_component_hash

def process_kicad_to_text(file_path, debug=False):
    """
    Process a KiCad schematic file and convert it to text representation
    
    Args:
        file_path: Path to the KiCad schematic file
        debug: Enable debug output
    """
    def analyze_schematics_recursive(file_path, base_path, depth=0, debug=False, parent_sheet=None):
        try:
            print("\n" + "-" * 80)
            if parent_sheet:
                print(f"Parent Sheet: {parent_sheet}")
            print(f"*******  {'  ' * depth}Analyzing: {file_path}  *******")
            schematic = Schematic().from_file(file_path)
            # print(f"Schematic object: {schematic}")
            analyze_schematic(schematic, base_path, debug=debug)

            # Process all sub-sheets recursively
            if schematic.sheets:
                print(f"{'  ' * depth}=== Sub-sheets found ===")
                for sheet in schematic.sheets:
                    sub_file_path = os.path.join(base_path, sheet.fileName.value)
                    # Recursively analyze the sub-schematic
                    analyze_schematics_recursive(sub_file_path, base_path, depth + 1, debug=debug, parent_sheet=file_path)
                    
        except Exception as e:
            print(f"{'  ' * depth}Error processing {file_path}: {str(e)}")

    # Process the schematic
    base_path = os.path.dirname(file_path)
    analyze_schematics_recursive(file_path, base_path, debug=debug)



def process_text_to_skidl(file_path, debug=False):
    """
    Process a text file containing component information and convert it to SKiDL code
    
    Args:
        file_path: Path to text file containing component information
        debug: Enable debug output
        
    Returns:
        List of parsed Component objects
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        components = []
        current_lines = []
        in_components_section = False
        seen_hashes = set()
        
        def process_current_component():
            if current_lines:
                result = parse_component_block(current_lines)
                if result.success:
                    component_hash = generate_component_hash(result.data)
                    if component_hash not in seen_hashes:
                        seen_hashes.add(component_hash)
                        components.append(result.data)
                    else:
                        print(f"Warning: Skipping duplicate component {result.data.reference}")
                else:
                    for error in result.errors:
                        print(f"Error parsing component: {error.message}")
        
        for line in lines:
            line = line.rstrip()
            
            # Start of components section
            if line == "=== Components ===":
                in_components_section = True
                continue
            
            if not in_components_section:
                continue
                
            # Start of new component or new section
            if line.startswith("Component:"):
                process_current_component()  # Process previous component if it exists
                current_lines = [line]
            elif line.startswith("==="):
                process_current_component()  # Process final component in section
                in_components_section = False
                current_lines = []
            elif line:  # Add non-empty lines to current component
                current_lines.append(line)
        
        # Process final component if exists
        process_current_component()
        
        # Print out the parsed components
        print("\nParsed Components:")
        for comp in components:
            print(f"Component: {comp.library}/{comp.name}")
            print(f"  Reference: {comp.reference}")
            print(f"  Value: {comp.value}")
            if comp.footprint:
                print(f"  Footprint: {comp.footprint}")
            if comp.datasheet:
                print(f"  Datasheet: {comp.datasheet}")
            if comp.description:
                print(f"  Description: {comp.description}")
            if comp.position:
                print(f"  Position: {comp.position}")
            if comp.angle is not None:
                print(f"  Angle: {comp.angle}")
        
        if not components:
            print("\nNo components were successfully parsed.")
            
        return components
        
    except Exception as e:
        print(f"Error processing text file: {str(e)}")
        return []
     

def main():
    """Main entry point for the KiCad schematic parser"""
    parser = argparse.ArgumentParser(
        description="KiCad Schematic Parser - Converts between KiCad schematics, text representation, and SKiDL code"
    )
    
    parser.add_argument(
        "file_path",
        help="Path to input file (KiCad schematic for kicad2text mode, text file for text2skidl mode)"
    )
    
    parser.add_argument(
        "--mode",
        choices=["kicad2text", "text2skidl"],
        default="kicad2text",
        help="Operation mode (default: kicad2text)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File not found: {args.file_path}")
        sys.exit(1)
    
    # Process based on mode
    if args.mode == "kicad2text":
        process_kicad_to_text(args.file_path, args.debug)
    else:  # text2skidl
        process_text_to_skidl(args.file_path, args.debug)

if __name__ == "__main__":
    main()
