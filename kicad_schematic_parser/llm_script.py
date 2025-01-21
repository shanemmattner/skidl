#!/usr/bin/env python3

#==============================================================================
# QUICK EDIT CONFIGURATION - Modify these values as needed
#==============================================================================

# Where to look for files
ROOT_DIRECTORY = "/Users/shanemattner/Desktop/skidl/kicad_schematic_parser"

# Where to save the combined output
OUTPUT_FILE = "query.txt"

# What files to collect (add or remove filenames as needed)
TARGET_FILES = [
    # Core Python Files
    'main.py',                    # Main entry point for schematic parsing
    'parser.py',                  # Core parsing logic
    'component_parser.py',        # Component and pin parsing
    'label_parser.py',           # Label parsing and connection logic 
    'geometry.py',               # Utility functions for geometric calculations
    
    # KiCad Schematic Files
    # 'example_kicad_project.kicad_sch',     # Top level schematic showing hierarchical sheets
    # 'labels_testing.kicad_sch',            # Sheet demonstrating label connections
    # 'power2.kicad_sch',                    # Sheet with power regulation circuit
    # 'resistor_divider.kicad_sch',          # Sheet with voltage divider circuit
    # 'stm32.kicad_sch',                     # Sheet with microcontroller circuit
    # 'wire_conn_test.kicad_sch',            # Sheet testing wire connections
    
    # Output Files
    'hierarchy.txt',              # Parser output showing hierarchical connections
    'labels_testing_output.txt',  # Parser output for label testing
    'debug_output.txt'            # Debug information from parser
]

INTRO_MESSAGE = """The following files are part of a circuit schematic parser project:

Core Python Files:
- main.py: Entry point that processes KiCad schematics and generates analysis
- parser.py: Core logic for parsing schematic files and analyzing connectivity
- component_parser.py: Handles parsing of components and their pins
- label_parser.py: Processes different types of labels and their connections
- geometry.py: Utility functions for geometric calculations

KiCad Schematic Files:
- example_kicad_project.kicad_sch: Top level schematic showing hierarchical connections
- labels_testing.kicad_sch: Test sheet for label connections
- power2.kicad_sch: Power regulation circuit
- resistor_divider.kicad_sch: Voltage divider circuit
- stm32.kicad_sch: Microcontroller circuit sheet
- wire_conn_test.kicad_sch: Test sheet for wire connections

Known Issues:
- Labels placed in the middle of a wire do not always get detected
- Labels might not transfer when connected to other labels
- Hierarchical labels with the same name are not always connected
  - Example: 3v3_monitor in wire_conn_test is separate from 3v3_monitor in stm32/labels_testing
  - Hierarchical labels only connect when explicitly connected through local labels or wires
  - In the example, stm32 and labels_testing 3v3_monitor connect through VDD_MONITOR local label

Key Connection Example:
The 3v3_monitor signal demonstrates how hierarchical labels work:
1. wire_conn_test sheet has its own isolated 3v3_monitor
2. stm32 sheet's 3v3_monitor (on PA6) connects to labels_testing's 3v3_monitor through the local label VDD_MONITOR
3. These are separate nets despite having the same hierarchical label name

Please help improve the label connection logic to handle these cases correctly.
"""

#==============================================================================
# Script Implementation - No need to modify below this line
#==============================================================================

"""
File Collector for Query Building

This script combines specific files into a single output file to help build
queries when iterating on software development. Edit the CONFIGURATION section
at the top to customize which files to collect.
"""

import os
from typing import List
from dataclasses import dataclass

@dataclass
class FileCollectorConfig:
    """Configuration class to store all script parameters"""
    root_directory: str
    output_filename: str
    target_filenames: List[str]
    intro_message: str

def create_config_from_settings() -> FileCollectorConfig:
    """Creates configuration object from the settings defined at the top of the script"""
    return FileCollectorConfig(
        root_directory=ROOT_DIRECTORY,
        output_filename=OUTPUT_FILE,
        target_filenames=TARGET_FILES,
        intro_message=INTRO_MESSAGE
    )

def is_target_file(filename: str, target_files: List[str]) -> bool:
    """
    Check if a filename matches one of our target filenames.
    
    Args:
        filename: Name of the file to check
        target_files: List of target filenames to match against
    """
    return os.path.basename(filename) in target_files

def find_target_files(config: FileCollectorConfig) -> List[str]:
    """
    Search for target files in the root directory, ignoring files in 'tests' folders.
    
    Args:
        config: Configuration object containing search parameters
    
    Returns:
        List[str]: List of full file paths for matching files
    """
    collected_files = []
    
    # Walk through the directory tree
    for dirpath, _, filenames in os.walk(config.root_directory):
        # Skip if 'tests' is in the directory path
        if 'tests' in dirpath.split(os.sep):
            continue
            
        for filename in filenames:
            if is_target_file(filename, config.target_filenames):
                full_path = os.path.join(dirpath, filename)
                if os.path.isfile(full_path):
                    collected_files.append(full_path)
    
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
                    
                    # Add clear separators around file content
                    out_file.write(f"\n/* Begin of file: {filename} */\n")
                    out_file.write(content)
                    out_file.write(f"\n/* End of file: {filename} */\n")
                    
                    # Print statistics for monitoring
                    num_lines = len(content.splitlines())
                    total_lines += num_lines
                    print(f"{filename}: {num_lines} lines")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        print(f"Total lines written: {total_lines}")

def main():
    """Main execution function"""
    # Create configuration from settings
    config = create_config_from_settings()
    
    # Find all matching files
    collected_files = find_target_files(config)
    
    # Combine files into output
    write_combined_file(collected_files, config)
    
    # Print summary
    print(f"\nProcessed {len(collected_files)} files")
    print(f"Output saved to: {config.output_filename}")

if __name__ == "__main__":
    main()
