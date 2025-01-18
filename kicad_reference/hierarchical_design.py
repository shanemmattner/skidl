from skidl import *

# Define power nets that will be shared across subcircuits
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False


# Generate netlist
generate_netlist()