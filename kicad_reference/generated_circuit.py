from skidl import *

# Define power nets that will be shared across subcircuits
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

@subcircuit
def resistor_divider(input_net):
    """
    Subcircuit for resistor_divider
    """
    # TODO: Add components and connections
    
    # Placeholder return
    return input_net

@subcircuit
def power2(input_net):
    """
    Subcircuit for power2
    """
    # TODO: Add components and connections
    
    # Placeholder return
    return input_net

# Instantiate the power nets
vcc_5v = Net('+5V')
vcc_5v.drive = POWER

# Instantiate the subcircuits
net_0 = resistor_divider(vcc_5v)
final_net = power2(net_0)

# Generate netlist
generate_netlist()