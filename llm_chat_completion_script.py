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
INTRO_MESSAGE = """Hierarchical Schematic Generation Issue Analysis

This collection of files demonstrates an issue with hierarchical schematic generation in SKiDL where parent-child relationships are not being maintained correctly in the generated KiCad schematics. In particular:

- We see that SKiDL's `circuit.group_name_cntr` does contain paths indicating parent-child subcircuits (e.g., 'top.single_resistor' and 'top.single_resistor0.two_resistors_circuit'), but the resulting KiCad files place each subcircuit at the top level rather than inside the correct parent sheet.

- Additionally, some SKiDL calls or versions append trailing numeric suffixes (e.g. 'single_resistor0'), which can result in hierarchy mismatches if the code only expects 'single_resistor'.

- Several unit tests fail for various reasons:
  * `test_blank_sch.py` fails when no subcircuits exist at all (empty `group_name_cntr`).
  * `test_nested_project.py` expects the final main schematic to have a hierarchical sheet referencing 'two_resistors_circuit', but it isn’t being nested.
  * `test_four_resistors.py`, `test_one_resistor.py`, and `test_two_resistors.py` check for existence of certain `.kicad_sch` files or the correct number of sheets/parts.

Key Observations & Problems:
1. **No Root Subcircuit**: If `group_name_cntr` is empty or if parent references like 'top' are missing, the code raises "No top-level subcircuit found." Some designs (e.g., blank or minimal) may not define any subcircuits.
2. **Mismatch of Hierarchy Strings**: SKiDL often uses 'subckt0', 'subckt1', etc. while `group_name_cntr` might store it without a trailing digit. Or the other way around. 
3. **Sheet Symbol Creation**: `gen_schematic_v8.py` tries to find each subcircuit's parent to embed it as a `(sheet ...)`, but if the parent path isn't in `group_name_cntr`, that subcircuit is treated as a new root. Hence multiple top-levels or incorrectly flattened structure.
4. **Template Handling**: The script copies a blank KiCad project from 'kicad_blank_project'. That part is working, but renaming might need special logic if there's only a single subcircuit or no subcircuits.

The test logs show many interesting scenarios, including:
- Single resistor only
- Two or four resistors
- Nested calls (like `single_resistor` calling `two_resistors_circuit`)
- Completely blank schematic where `group_name_cntr` is empty
- Tests that expect the main schematic to have a single hierarchical sheet
- Tests that expect a `.kicad_sch` file named after the subcircuit.

Potential Next Steps / Debugging Strategies:
- **Handle the Empty Subcircuit Case** gracefully by generating a blank `.kicad_sch` or skipping the "No root found" error if `group_name_cntr` is empty.
- **Refine Hierarchy Matching** for trailing digits so it only changes paths that truly need it.
- **Embed Child Subcircuits** inside the parent's `.kicad_sch` if the parent path partially matches or if SKiDL indicates nesting (like `top.subckt0.child_subckt`).
- **Optionally** create a dedicated top-level `.kicad_sch` that references each root subcircuit, if that’s needed by the test.

Below are the files that demonstrate the current logic and test environment. By combining them into a single reference, we can continue to iterate on the approach to fix hierarchical sheet generation.

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
