#!/usr/bin/env python3
import sys
import os
import argparse
from kiutils.schematic import Schematic
from kicad_hierarchy_parser import analyze_schematic
from skidl_generator.component_parser.component_parser import parse_component_name, parse_component_properties

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
        file_path: Path to the text file containing component information
        debug: Enable debug output
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Process components
        current_component = None
        property_lines = []
        components = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Component:"):
                # Process previous component if exists
                if current_component and property_lines:
                    prop_result = parse_component_properties(property_lines, line_num=i-len(property_lines))
                    if prop_result.success:
                        components.append(prop_result.data)
                    else:
                        for error in prop_result.errors:
                            print(f"Error parsing properties: {error.message}")
                
                # Start new component
                result = parse_component_name(line, line_num=i+1)
                if result.success:
                    current_component = result.data
                    property_lines = []
                else:
                    print(f"Error parsing component name: {result.errors[0].message}")
                    
            elif line == "Properties:":
                property_lines = [line]
            elif current_component and property_lines:
                property_lines.append(line)
        
        # Process final component if exists
        if current_component and property_lines:
            prop_result = parse_component_properties(property_lines)
            if prop_result.success:
                components.append(prop_result.data)
            else:
                for error in prop_result.errors:
                    print(f"Error parsing properties: {error.message}")
        
        # Print results
        print("\nParsed Components:")
        for comp in components:
            print(f"\nReference: {comp.reference}")
            print(f"Value: {comp.value}")
            if comp.footprint:
                print(f"Footprint: {comp.footprint}")
            if comp.library:
                print(f"Library: {comp.library}")
            if comp.name:
                print(f"Name: {comp.name}")
                
    except Exception as e:
        print(f"Error processing text file: {str(e)}")

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
