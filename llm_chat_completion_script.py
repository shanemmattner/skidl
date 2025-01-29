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
    'test.kicad_sch',
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
- `test.kicad_sch`: Generated KiCad schematic file for a test circuit

Here is the current output of the logic:
venvshanemattner@Shanes-MacBook-Pro skidl % python3 src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py
INFO: Using KiCad blank project directory: ./kicad_blank_project @ [/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
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
[  MATCH   ] Found component J1 in esp32s3mini1
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : J1
[   COMP   ] Library   : Connector_Generic
[   COMP   ] Name      : Conn_02x03_Odd_Even
[   COMP   ] Value     : Conn_02x03_Odd_Even
[   COMP   ] Sheet     : esp32s3mini1
[   COMP   ] Pins      : 6
[   COMP   ] Footprint : Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : J1
[  PLACE   ] Position   : (20.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol J1 to schematic
[  MATCH   ] Found component U1 in esp32s3mini1
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : U1
[   COMP   ] Library   : RF_Module
[   COMP   ] Name      : ESP32-S3-MINI-1
[   COMP   ] Value     : ESP32-S3-MINI-1
[   COMP   ] Sheet     : esp32s3mini1
[   COMP   ] Pins      : 65
[   COMP   ] Footprint : RF_Module:ESP32-S2-MINI-1
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : U1
[  PLACE   ] Position   : (40.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol U1 to schematic
[   SKIP   ] C2 (in resistor_divider1)
[   SKIP   ] R1 (in resistor_divider1)
[   SKIP   ] R2 (in resistor_divider1)
[   SKIP   ] C3 (in 3v3_regulator)
[   SKIP   ] C4 (in 3v3_regulator)
[   SKIP   ] C5 (in 3v3_regulator)
[   SKIP   ] C6 (in 3v3_regulator)
[   SKIP   ] R3 (in 3v3_regulator)
[   SKIP   ] R4 (in 3v3_regulator)
[   SKIP   ] R5 (in 3v3_regulator)
[   SKIP   ] R6 (in 3v3_regulator)
[   SKIP   ] U2 (in 3v3_regulator)
[   SKIP   ] C7 (in USB)
[   SKIP   ] P1 (in USB)
[   SKIP   ] R7 (in USB)
[  SHEET   ] Found 3 components in esp32s3mini1
INFO: Generated schematic for esp32s3mini1 at ./kicad_blank_project/esp32s3mini1.kicad_sch @ [/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
Generated schematic for esp32s3mini1 at ./kicad_blank_project/esp32s3mini1.kicad_sch
[  SHEET   ] Looking for components in sheet: resistor_divider1
[   SKIP   ] C1 (in esp32s3mini1)
[   SKIP   ] J1 (in esp32s3mini1)
[   SKIP   ] U1 (in esp32s3mini1)
[  MATCH   ] Found component C2 in resistor_divider1
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C2
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 100nF
[   COMP   ] Sheet     : resistor_divider1
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C2
[  PLACE   ] Position   : (0.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C2 to schematic
[  MATCH   ] Found component R1 in resistor_divider1
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R1
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 1k
[   COMP   ] Sheet     : resistor_divider1
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R1
[  PLACE   ] Position   : (20.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R1 to schematic
[  MATCH   ] Found component R2 in resistor_divider1
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R2
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 2k
[   COMP   ] Sheet     : resistor_divider1
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R2
[  PLACE   ] Position   : (40.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R2 to schematic
[   SKIP   ] C3 (in 3v3_regulator)
[   SKIP   ] C4 (in 3v3_regulator)
[   SKIP   ] C5 (in 3v3_regulator)
[   SKIP   ] C6 (in 3v3_regulator)
[   SKIP   ] R3 (in 3v3_regulator)
[   SKIP   ] R4 (in 3v3_regulator)
[   SKIP   ] R5 (in 3v3_regulator)
[   SKIP   ] R6 (in 3v3_regulator)
[   SKIP   ] U2 (in 3v3_regulator)
[   SKIP   ] C7 (in USB)
[   SKIP   ] P1 (in USB)
[   SKIP   ] R7 (in USB)
[  SHEET   ] Found 3 components in resistor_divider1
INFO: Generated schematic for resistor_divider1 at ./kicad_blank_project/resistor_divider1.kicad_sch @ [/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
Generated schematic for resistor_divider1 at ./kicad_blank_project/resistor_divider1.kicad_sch
[  SHEET   ] Looking for components in sheet: _3v3_regulator
[   SKIP   ] C1 (in esp32s3mini1)
[   SKIP   ] J1 (in esp32s3mini1)
[   SKIP   ] U1 (in esp32s3mini1)
[   SKIP   ] C2 (in resistor_divider1)
[   SKIP   ] R1 (in resistor_divider1)
[   SKIP   ] R2 (in resistor_divider1)
[  MATCH   ] Found component C3 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C3
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 10uF
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C3
[  PLACE   ] Position   : (0.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C3 to schematic
[  MATCH   ] Found component C4 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C4
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 10uF
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C4
[  PLACE   ] Position   : (20.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C4 to schematic
[  MATCH   ] Found component C5 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C5
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 100nF
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C5
[  PLACE   ] Position   : (40.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C5 to schematic
[  MATCH   ] Found component C6 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C6
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 100nF
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C6
[  PLACE   ] Position   : (60.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C6 to schematic
[  MATCH   ] Found component R3 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R3
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 2k
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R3
[  PLACE   ] Position   : (80.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R3 to schematic
[  MATCH   ] Found component R4 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R4
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 1k
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R4
[  PLACE   ] Position   : (0.0, -20.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R4 to schematic
[  MATCH   ] Found component R5 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R5
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 1k
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R5
[  PLACE   ] Position   : (20.0, -20.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R5 to schematic
[  MATCH   ] Found component R6 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R6
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 2k
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R6
[  PLACE   ] Position   : (40.0, -20.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R6 to schematic
[  MATCH   ] Found component U2 in _3v3_regulator
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : U2
[   COMP   ] Library   : Regulator_Linear
[   COMP   ] Name      : NCP1117-3.3_SOT223
[   COMP   ] Value     : NCP1117-3.3_SOT223
[   COMP   ] Sheet     : 3v3_regulator
[   COMP   ] Pins      : 3
[   COMP   ] Footprint : Package_TO_SOT_SMD:SOT-223-3_TabPin2
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : U2
[  PLACE   ] Position   : (60.0, -20.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol U2 to schematic
[   SKIP   ] C7 (in USB)
[   SKIP   ] P1 (in USB)
[   SKIP   ] R7 (in USB)
[  SHEET   ] Found 9 components in _3v3_regulator
INFO: Generated schematic for _3v3_regulator at ./kicad_blank_project/_3v3_regulator.kicad_sch @ [/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
Generated schematic for _3v3_regulator at ./kicad_blank_project/_3v3_regulator.kicad_sch
[  SHEET   ] Looking for components in sheet: USB
[   SKIP   ] C1 (in esp32s3mini1)
[   SKIP   ] J1 (in esp32s3mini1)
[   SKIP   ] U1 (in esp32s3mini1)
[   SKIP   ] C2 (in resistor_divider1)
[   SKIP   ] R1 (in resistor_divider1)
[   SKIP   ] R2 (in resistor_divider1)
[   SKIP   ] C3 (in 3v3_regulator)
[   SKIP   ] C4 (in 3v3_regulator)
[   SKIP   ] C5 (in 3v3_regulator)
[   SKIP   ] C6 (in 3v3_regulator)
[   SKIP   ] R3 (in 3v3_regulator)
[   SKIP   ] R4 (in 3v3_regulator)
[   SKIP   ] R5 (in 3v3_regulator)
[   SKIP   ] R6 (in 3v3_regulator)
[   SKIP   ] U2 (in 3v3_regulator)
[  MATCH   ] Found component C7 in USB
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : C7
[   COMP   ] Library   : Device
[   COMP   ] Name      : C
[   COMP   ] Value     : 10uF
[   COMP   ] Sheet     : USB
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Capacitor_SMD:C_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : C7
[  PLACE   ] Position   : (0.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol C7 to schematic
[  MATCH   ] Found component P1 in USB
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : P1
[   COMP   ] Library   : Connector
[   COMP   ] Name      : USB_C_Plug_USB2.0
[   COMP   ] Value     : USB_C_Plug_USB2.0
[   COMP   ] Sheet     : USB
[   COMP   ] Pins      : 13
[   COMP   ] Footprint : Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : P1
[  PLACE   ] Position   : (20.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol P1 to schematic
[  MATCH   ] Found component R7 in USB
[   COMP   ] ----------------------------------------
[   COMP   ] Reference : R7
[   COMP   ] Library   : Device
[   COMP   ] Name      : R
[   COMP   ] Value     : 5.1K
[   COMP   ] Sheet     : USB
[   COMP   ] Pins      : 2
[   COMP   ] Footprint : Resistor_SMD:R_0603_1608Metric
[   COMP   ] ----------------------------------------
[  PLACE   ] ----------------------------------------
[  PLACE   ] Component  : R7
[  PLACE   ] Position   : (40.0, -0.0)
[  PLACE   ] Grid Size  : 20.0
[  PLACE   ] ----------------------------------------
[  SYMBOL  ] Adding symbol R7 to schematic
[  SHEET   ] Found 3 components in USB
INFO: Generated schematic for USB at ./kicad_blank_project/USB.kicad_sch @ [/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
Generated schematic for USB at ./kicad_blank_project/USB.kicad_sch
INFO: Added sheet symbols to main schematic at ./kicad_blank_project/kicad_blank_project.kicad_sch @ [/Users/shanemattner/Desktop/skidl/src/skidl/tools/kicad8/sch_gen/example_kicad_project_SKIDL/kicad_project_SKIDL/main.py:26]
INFO: No errors or warnings found while generating schematic.

venvshanemattner@Shanes-MacBook-Pro skidl % 
----

Current issues:
- the logic produces a kicad_blank_project directory, and kicad_blank_project.kicad_sch has hierarchical sheets for the subcircuits, but the subcircuit sheets are not generated
- test.kicad_sch is generated in the same directory as kicad_blank_project and seems to contain the parts for a USB circuit.

Feature requests:
- user input name for the project, instead of "kicad_blank_project"

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
