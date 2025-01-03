#!/usr/bin/env python3

#==============================================================================
# QUICK EDIT CONFIGURATION - Modify these values as needed
#==============================================================================

# Where to look for files
ROOT_DIRECTORY = "/Users/shanemattner/Desktop/skidl"

# Where to save the combined output
OUTPUT_FILE = "collected_code.txt"

# What files to collect (add or remove filenames as needed)
TARGET_FILES = {
    'gen_schematic.py': ['kicad5', 'kicad6', 'kicad7', 'kicad8'],
    'kicad_sch_writer.py': None,
    's-expressions.md': None,
    'Schematic_File_Format.md': None,
}

# Message to add at the start of the output file
INTRO_MESSAGE = """
Help me develop code for generating KiCad schematics from SKiDL scripts for KiCAD 8.  SKiDL is a Python package that allows you to design electronic circuits using Python code. 

File Descriptions:
- gen_schematic.py: Python files used to generate a KiCad schematic from a SKiDL script. Only KiCAD version 6 and 5 are supported. Please reference KiCAD 6 for building new logic
- kicad_sch_writer.py: Python module to write KiCad schematic files
- s-expressions.md: Documentation on the S-expression format used in KiCad files
- Schematic_File_Format.md: Documentation on the KiCad schematic file format
"""

#==============================================================================
# Script Implementation - No need to modify below this line
#==============================================================================

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class FileCollectorConfig:
    """Configuration class to store all script parameters"""
    root_directory: str
    output_filename: str
    target_files: Dict[str, Optional[List[str]]]
    intro_message: str

def create_config_from_settings() -> FileCollectorConfig:
    """Creates configuration object from the settings defined at the top of the script"""
    return FileCollectorConfig(
        root_directory=ROOT_DIRECTORY,
        output_filename=OUTPUT_FILE,
        target_files=TARGET_FILES,
        intro_message=INTRO_MESSAGE
    )

def is_target_file(filepath: str, target_files: Dict[str, Optional[List[str]]]) -> bool:
    """
    Check if a filepath matches our target criteria.
    
    Args:
        filepath: Full path of the file to check
        target_files: Dictionary of target filenames and their optional subdirectory constraints
    """
    filename = os.path.basename(filepath)
    
    # Debug print
    print(f"Checking file: {filepath}")
    
    if filename not in target_files:
        return False
        
    # If no subdirectory constraints, accept the file
    if target_files[filename] is None:
        print(f"Found unconstrained target file: {filepath}")
        return True
        
    # Check if file is in any of the specified subdirectories
    filepath_parts = filepath.split(os.sep)
    for subdir in target_files[filename]:
        if subdir in filepath_parts:
            print(f"Found constrained target file: {filepath} (matches {subdir})")
            return True
            
    return False

def find_target_files(config: FileCollectorConfig) -> List[str]:
    """
    Search for target files in the root directory.
    
    Args:
        config: Configuration object containing search parameters
    
    Returns:
        List[str]: List of full file paths for matching files
    """
    collected_files = []
    
    print(f"\nSearching in root directory: {config.root_directory}")
    print(f"Looking for files: {list(config.target_files.keys())}\n")
    
    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(config.root_directory):
        print(f"\nExamining directory: {dirpath}")
        print(f"Contains directories: {dirnames}")
        print(f"Contains files: {filenames}")
        
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if os.path.isfile(full_path) and is_target_file(full_path, config.target_files):
                collected_files.append(full_path)
                print(f"Added to collection: {full_path}")
    
    return sorted(collected_files)

def write_combined_file(collected_files: List[str], config: FileCollectorConfig) -> None:
    """
    Write all collected file contents to a single output file.
    
    Args:
        collected_files: List of file paths to combine
        config: Configuration object containing output settings
    """
    with open(config.output_filename, 'w') as out_file:
        # Write the introduction message
        out_file.write(config.intro_message + "\n")
        
        # Process each collected file
        total_lines = 0
        for file_path in collected_files:
            try:
                # Read and write each file's contents with clear separation
                with open(file_path, 'r') as input_file:
                    content = input_file.read()
                    filename = os.path.basename(file_path)
                    relative_path = os.path.relpath(file_path, config.root_directory)
                    
                    # Add clear separators around file content
                    out_file.write(f"\n/* Begin of file: {relative_path} */\n")
                    out_file.write(content)
                    out_file.write(f"\n/* End of file: {relative_path} */\n")
                    
                    # Print statistics for monitoring
                    num_lines = len(content.splitlines())
                    total_lines += num_lines
                    print(f"{relative_path}: {num_lines} lines")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        print(f"Total lines written: {total_lines}")

def main():
    """Main execution function"""
    # Create configuration from settings
    config = create_config_from_settings()
    
    # Find all matching files
    collected_files = find_target_files(config)
    
    if not collected_files:
        print("\nNo matching files found! Check your ROOT_DIRECTORY and TARGET_FILES settings.")
        return
        
    print("\nFound files:")
    for f in collected_files:
        print(f"- {f}")
        
    # Combine files into output
    print("\nWriting combined output file...")
    write_combined_file(collected_files, config)
    
    # Print summary
    print(f"\nProcessed {len(collected_files)} files")
    print(f"Output saved to: {config.output_filename}")

if __name__ == "__main__":
    main()