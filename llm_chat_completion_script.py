#!/usr/bin/env python3

#==============================================================================
# QUICK EDIT CONFIGURATION - Modify these values as needed
#==============================================================================

# Where to look for files
ROOT_DIRECTORY = "/Users/shanemattner/Desktop/skidl"

# Where to save the combined output
OUTPUT_FILE = "collected_code.txt"

# What files to collect (add or remove filenames as needed)
TARGET_FILES = [
    # Core Implementation Files
    'gen_schematic_v8.py',      # Main schematic generation logic
    'kicad_writer.py',          # KiCad schematic file writer
    
    # Test and Example Files
    'test_circuits.py',         # Shows current hierarchical issue
    'test_nested_project.py',   # Reference implementation for proper nesting
    
    # Generated Schematics Showing Issue
    'testing_hierarchy.kicad_sch',      # Main project schematic
    'single_resistor.kicad_sch',        # Parent circuit
    'two_resistors_circuit.kicad_sch',  # Child circuit that should be nested
    
    # Reference Implementation
    'nested_project.kicad_sch',  # Shows correct hierarchical structure
]

# Message to add at the start of the output file
INTRO_MESSAGE = """Hierarchical Schematic Generation Issue Analysis

This collection of files demonstrates an issue with hierarchical schematic generation in SKiDL where parent-child relationships between circuits are not being maintained in the generated KiCad schematics.

Current Behavior:
- SKiDL Circuit object correctly tracks hierarchy in group_name_cntr:
  {
      'top.single_resistor': 1,
      'top.single_resistor0.two_resistors_circuit': 1
  }
- However, generated KiCad schematics show all circuits at the top level instead of maintaining proper nesting

Core Implementation Files:
- gen_schematic_v8.py: Main schematic generation logic that processes circuit hierarchy
- kicad_writer.py: Handles writing KiCad schematic files and sheet symbols

Test Files:
- test_circuits.py: Demonstrates the issue with a nested circuit structure:
  * single_resistor() is the parent circuit
  * two_resistors_circuit() is called within single_resistor()
- test_nested_project.py: Reference implementation showing proper hierarchical sheet handling

Generated Schematics:
- testing_hierarchy.kicad_sch: Main project schematic
- single_resistor.kicad_sch: Parent circuit containing one resistor
- two_resistors_circuit.kicad_sch: Child circuit that should be nested under single_resistor

Reference Implementation:
- nested_project.kicad_sch: Shows correct hierarchical structure with proper sheet paths and instances

Terminal Output:
[Include the terminal output showing the issue]

Key Areas to Analyze:
1. How circuit hierarchy is tracked in SKiDL's Circuit object
2. Sheet symbol creation in gen_schematic_v8.py
3. Project configuration updates for proper sheet paths
4. KiCad schematic file structure for hierarchical sheets
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
    Search for target files in the root directory.
    
    Args:
        config: Configuration object containing search parameters
    
    Returns:
        List[str]: List of full file paths for matching files
    """
    collected_files = []
    
    # Walk through the directory tree
    for dirpath, _, filenames in os.walk(config.root_directory):
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
