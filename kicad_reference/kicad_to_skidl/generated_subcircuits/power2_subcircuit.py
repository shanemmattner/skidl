from skidl import *

# Define ground net
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

@subcircuit
def power2(pwr_net):
    """Create a power2 subcircuit"""
    # Create power nets
    vcc_3v3 = Net('+3V3')
    vcc_3v3.drive = POWER
        # Create components
    u1 = Part("Regulator_Linear", "NCP1117-3.3_SOT223", footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    c2 = Part("Device", "C", value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')

    # Connect the components
    # Connect regulator input
    pwr_net += u1['VI']
    u1['GND'] += gnd
    u1['VO'] += vcc_3v3

    # Connect input capacitor
    pwr_net += c2[1]
    c2[2] += gnd

    return vcc_3v3
