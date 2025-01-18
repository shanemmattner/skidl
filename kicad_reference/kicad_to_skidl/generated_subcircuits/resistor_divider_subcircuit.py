from skidl import *

# Define ground net
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

@subcircuit
def resistor_divider(pwr_net):
    """Create a resistor_divider subcircuit"""
    # Create components
    r1 = Part("Device", "R", value='1K', footprint='Resistor_SMD:R_0603_1608Metric')

    # Connect the components
    # Connect single resistor
    pwr_net & r1 & gnd

    return pwr_net