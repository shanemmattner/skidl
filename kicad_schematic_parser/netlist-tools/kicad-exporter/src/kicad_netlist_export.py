#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys
from pathlib import Path

def get_kicad_cli_path():
    """Get KiCad CLI path from environment variable or default installation"""
    env_path = os.environ.get('KICAD8_SYMBOL_DIR', '').replace('symbols', 'kicad-cli')
    if env_path and Path(env_path).exists():
        return env_path
        
    default_path = '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
    if Path(default_path).exists():
        return default_path
        
    raise FileNotFoundError("KiCad CLI not found. Set KICAD8_SYMBOL_DIR or install KiCad kicadsexpr")

def main():
    parser = argparse.ArgumentParser(description='Export KiCad schematic to KiCAD ')
    parser.add_argument('schematic', help='Path to KiCad schematic file (.kicad_sch)')
    parser.add_argument('-o', '--output', help='Output netlist path (.net)')

    args = parser.parse_args()
    
    try:
        schematic_path = Path(args.schematic)
        if not schematic_path.exists():
            raise FileNotFoundError(f"Schematic file not found: {schematic_path}")

        output_path = Path(args.output) if args.output else schematic_path.with_suffix('.net')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        kicad_cli = get_kicad_cli_path()
        
        result = subprocess.run(
            [kicad_cli, 'sch', 'export', 'netlist',
             '--format', 'kicadsexpr',
             '--output', str(output_path),
             str(schematic_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Export failed:\n{result.stderr}")
            
        print(f"Successfully exported netlist to {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
