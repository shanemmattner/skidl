import os
from skidl import *

# Set KiCad symbol library path 
os.environ['KICAD8_SYMBOL_DIR'] = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'

# Set default tool to KiCad 8
set_default_tool('kicad8') 

# Create circuit
circ = Circuit()

# Load KiCad library
lib = SchLib('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym', tool='kicad8')

# Create nets
gnd = Net('GND')
vcc = Net('VCC')

# Create resistor and add to circuit
r_10k = Part(lib, "R", footprint="Resistor_SMD:R_0603_1608Metric", value="10k")
r_10k.parse()

# Load symbol drawing data
from skidl.tools.kicad8.gen_schematic import load_symbol_drawing_data
syminfo = load_symbol_drawing_data('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym')

# Convert drawing data to expected format 
# The code expects drawing data per unit as a list
r_10k.draw = [syminfo['R']]  # Wrap in list since R has one unit

# Connect resistor
r_10k[1] += vcc
r_10k[2] += gnd

# Preprocess circuit
from skidl.tools.kicad8.gen_schematic import preprocess_circuit
preprocess_circuit(default_circuit)

# Generate schematic
generate_schematic(tool='kicad8')