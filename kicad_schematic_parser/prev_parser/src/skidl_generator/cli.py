"""Command line interface for schematic to SKiDL conversion."""

import argparse
from .sheet_to_skidl import sheet_to_skidl

def main():
    parser = argparse.ArgumentParser(description='Convert KiCad schematic sheet to SKiDL code')
    parser.add_argument('input', help='Input text file containing schematic description')
    parser.add_argument('output', help='Output Python file for SKiDL code')
    parser.add_argument('--name', default='circuit', help='Name for the generated subcircuit')
    
    args = parser.parse_args()
    
    with open(args.input) as f:
        text = f.read()
    
    skidl_code = sheet_to_skidl(args.name, text)
    
    with open(args.output, 'w') as f:
        f.write(skidl_code)

if __name__ == '__main__':
    main()
