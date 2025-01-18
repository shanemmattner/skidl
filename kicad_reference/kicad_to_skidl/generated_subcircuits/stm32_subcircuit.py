from skidl import *

# Define ground net
gnd = Net('GND')
gnd.drive = POWER
gnd.do_erc = False

@subcircuit
def stm32(pwr_net):
    """Create a stm32 subcircuit"""
    # Create components
    c1 = Part("Device", "C", value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    u2 = Part("MCU_ST_STM32G4", "STM32G431C6Ux", footprint='Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm')

    # Connect the components
    # Connect MCU power pins
    pwr_net += u2['VDD']
    u2['VSS'] += gnd
    u2['VSSA'] += gnd
    u2['VDDA'] += pwr_net

    return pwr_net