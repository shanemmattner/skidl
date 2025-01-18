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
    r2 = Part("Device", "R", value='1K', footprint='Resistor_SMD:R_0603_1608Metric')

    # Create internal connection nodes
    r1_2_r2_1 = Net('R1_2-R2_1')

    # Connect the components
    # Connect power to first resistor
    pwr_net & r1

    # Connect divider node
    r1 & r1_2_r2_1
    r1_2_r2_1 & r2

    # Connect to ground
    r2 & gnd

    # Return just the divider node, not all locals
    return r1_2_r2_1