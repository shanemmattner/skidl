#!/usr/bin/env python3

#==============================================================================
# QUICK EDIT CONFIGURATION - Modify these values as needed
#==============================================================================

# Where to look for files
ROOT_DIRECTORY = "/Users/shanemattner/Desktop/skidl"

# Where to save the combined output
OUTPUT_FILE = "collected_code.txt"

# What files to collect (add or remove filenames as needed)
# Expanded to include additional test files encountered in the logs.
TARGET_FILES = [
    # Core Implementation Files
    'gen_schematic_v8.py',      # Main schematic generation logic
    'kicad_writer.py',          # KiCad schematic file writer
    
    # Test and Example Files
    'test_circuits.py',         # Shows current hierarchical issue
    'test_nested_project.py',   # Reference implementation for proper nesting
    'test_blank_sch.py',        # Tests blank schematic generation & metadata
    'test_four_resistors.py',   # Tests a 4-resistor subcircuit
    'test_one_resistor.py',     # Tests a single resistor subcircuit
    'test_two_resistors.py',    # Tests a 2-resistor subcircuit
    
    # Generated Schematics Showing Issue
    'testing_hierarchy.kicad_sch',      # Main project schematic
    'single_resistor.kicad_sch',        # Parent circuit
    'two_resistors_circuit.kicad_sch',  # Child circuit that should be nested
    
    # Reference Implementation
    'nested_project.kicad_sch',  # Shows correct hierarchical structure
]

# Message to add at the start of the output file
INTRO_MESSAGE = """

Hierarchical Schematic Generation Issue Analysis - Updated Status

Current State:
We have implemented a HierarchyManager class that correctly:
- Handles path normalization for sheet naming
- Creates the top-level schematic with sheet symbols
- Sets up the basic file structure

However, there are still critical issues:

1. **Part Assignment Issue**:
- Parts are not being correctly assigned to their circuit sheets
- Example: A single resistor circuit generates the sheet but no components appear
- Key files to examine: `hierarchy_manager.py` (assign_parts_to_circuits method)
- Path normalization may be failing to match parts to their circuits

2. **Hierarchy Building**:
- Current paths ['top.single_resistor', 'top.single_resistor0.two_resistors_circuit']
- Two-resistor circuit should be nested under single_resistor0 but appears missing
- Key files to examine: 
  * `hierarchy_manager.py` (build_hierarchy method)
  * `gen_schematic_v8.py` (hierarchy parsing)

3. **Sheet Generation**:
- Only generating single_resistor.kicad_sch
- Missing two_resistors_circuit.kicad_sch generation
- Key files to examine: `hierarchy_manager.py` (_generate_circuit_schematic method)

Debugging Priority:
1. First fix part assignment by debugging the path matching in assign_parts_to_circuits()
2. Then examine hierarchy building to ensure child circuits are properly nested
3. Finally verify sheet generation for all circuits in the hierarchy

Key Methods to Focus On:
- HierarchyManager.normalize_path_for_matching()
- HierarchyManager.assign_parts_to_circuits()
- HierarchyManager._generate_circuit_schematic()

Next Steps:
1. Add debug logging in assign_parts_to_circuits() to track:
   - Raw hierarchy path of each part
   - Normalized paths being compared
   - Which node matches (or fails to match)
2. Verify the parent-child relationships in build_hierarchy()
3. Add checks to ensure _generate_circuit_schematic() is called for all nodes

The core issue appears to be in the path normalization and matching logic, as parts aren't being assigned to their correct circuit nodes despite the sheets being created.
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
