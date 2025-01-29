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
    'kicad_library_parser.py',
    'kicad_symbol_adder.py',
    'kicad_writer.py',
    'symbol_definitions.py',
    'symbol_flatten.py',
    'symbol_parser.py',
    'gen_schematic_v8.py',
    '_3v3_regulator_GOOD.kicad_sch',
    '_3v3_regulator.kicad_sch',
    'NCP1117-3.3_SOT223_library_symbol.txt',
    # 'Schematic_File_Format.md',
    # 'sch_io_kicad_sexpr_common.cpp',
    # 'sch_io_kicad_sexpr_lib_cache.cpp',
    # 'sch_io_kicad_sexpr_parser.cpp',
    # 'sch_io_kicad_sexpr.cpp',
    'SCH_GEN_ISSUE_SUMMARY.md',
]

# Message to add at the start of the output file
INTRO_MESSAGE = """The following files are part of a software project:
This collection of files for a circuit design tool includes Python scripts and KiCad schematic files.

Core Files:
- kicad_symbol_adder.py: Python script to add KiCad symbols to schematic files
- symbol_parser.py: Python script to parse KiCad symbol files
- _3v3_regulator_GOOD.kicad_sch: manually created KiCad schematic for a 3.3V regulator circuit, this is the correct schematic file
- _3v3_regulator.kicad_sch: generated KiCad schematic for a 3.3V regulator circuit, this is the incorrect schematic file
- NCP1117-3.3_SOT223_library_symbol.txt: text file containing the KiCad symbol for the part in question 3.3V regulator
- Schematic_File_Format.md: documentation on the format of KiCad schematic files
- sch_io_kicad_sexpr_common.cpp: C++ source file for reading and writing KiCad schematic files
- sch_io_kicad_sexpr_lib_cache.cpp: C++ source file for caching KiCad library symbols
- sch_io_kicad_sexpr_parser.cpp: C++ source file for parsing KiCad schematic files
- sch_io_kicad_sexpr.cpp: C++ source file for handling KiCad schematic file I/O
- SCH_GEN_ISSUE_SUMMARY.md: summary of issues related to generating KiCad schematic files
- `kicad_writer.py`: Generates `.kicad_sch` files by parsing symbols, flattening inheritance, and placing components.
- `gen_schematic_v8.py`: Main script to generate schematics, handling subcircuits, placement, and sheet hierarchy.
- `symbol_definitions.py`: Defines symbol structures, including properties, pins, and shapes.
- `kicad_library_parser.py`: Parses KiCad `.kicad_sym` library files to extract symbol definitions.
- `symbol_flatten.py`: Flattens symbols by resolving inherited properties and structures.


Help me debug this code to generate kicad schematics from python code.  Currently I get this error:

venvshanemattner@Shanes-MacBook-Pro skidl % python3 example_kicad_project_SKIDL/kicad_project_SKIDL/main.py
INFO: Using KiCad blank project directory: ./kicad_blank_project @ [/Users/shanemattner/Desktop/skidl/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
[  SHEET   ] Looking for components in sheet: esp32s3mini1
[  MATCH   ] Found component C1 in esp32s3mini1
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C1
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 10uF
[   COMP   ] Sheet     : esp32s3mini1
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C1
[  PLACE   ] Position   : (0.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C1 to schematic
Traceback (most recent call last):
  File "/Users/shanemattner/Desktop/skidl/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py", line 26, in <module>
    generate_schematic()
    ~~~~~~~~~~~~~~~~~~^^
  File "/Users/shanemattner/Desktop/skidl/src/skidl/circuit.py", line 1006, in generate_schematic
    tool_modules[tool].gen_schematic(self, **kwargs)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/gen_schematic.py", line 143, in gen_schematic
    writer.add_symbol(symbol)
    ^^^^^^^^^^^^^^^^^
AttributeError: 'KicadSchematicWriter' object has no attribute 'add_symbol'
venvshanemattner@Shanes-MacBook-Pro skidl % 

_______

The code for gen_schematic.py needs to be updated to follow the rest of the logic.  While reviewing the other logic I found that some of the required fields are missing, like footprints, rotation, 
and other fields.  I will need to update the code to include these fields. 

Please check that all logic works together cohesively.  Ask me question if you are not sure about something.

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
