from skidl import *

# Define power nets that will be shared across subcircuits
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

from resistor_divider_subcircuit import resistor_divider
from power2_subcircuit import power2

# Instantiate the power nets
vcc_5v = Net('+5V')
vcc_5v.drive = POWER

# Instantiate the subcircuits
net_0 = resistor_divider(vcc_5v)
final_net = power2(net_0)

# Generate netlist
generate_netlist()