#!/usr/bin/env python3

import re
import sys

def read_schematic_file(filepath):
    """Read and return the content of a KiCad schematic file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def extract_sheet_names(content):
    """
    Extract sheet names from KiCad schematic content.
    
    Args:
        content (str): Content of the .kicad_sch file
        
    Returns:
        list: List of sheet names found in the file
    """
    if not content:
        return []
            
    # Pattern matches: (property "Sheetname" "name_here"
    pattern = r'\(property\s+"Sheetname"\s+"([^"]+)"'
    
    # Find all matches and extract the sheet names
    return re.findall(pattern, content)

def extract_sheet_files(content):
    """
    Extract sheet file paths from KiCad schematic content.
    
    Args:
        content (str): Content of the .kicad_sch file
        
    Returns:
        list: List of sheet file paths found in the file
    """
    if not content:
        return []
            
    # Pattern matches: (property "Sheetfile" "path_here"
    pattern = r'\(property\s+"Sheetfile"\s+"([^"]+)"'
    
    # Find all matches and extract the sheet file paths
    return re.findall(pattern, content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python kicad_sheet_parser.py <path_to_kicad_sch_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    content = read_schematic_file(filepath)
    
    if content is None:
        sys.exit(1)
        
    sheet_names = extract_sheet_names(content)
    sheet_files = extract_sheet_files(content)
    
    if sheet_names and sheet_files:
        print("\nSheet information found:")
        for name, file in zip(sheet_names, sheet_files):
            print(f"- Name: {name}")
            print(f"  File: {file}")
    else:
        print("No sheet information found in the file")

if __name__ == "__main__":
    main()
