from skidl import *

@subcircuit
def power_3v3_reg(vin_5v):
    """Power regulation with monitoring"""
    # Create regulator and caps
    reg = Part('Regulator_Linear', 'NCP1117-3.3_SOT223', 
               footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    c_in = Part('Device', 'C', value='10uF',
                footprint='Capacitor_SMD:C_0603_1608Metric')
    c_out = Part('Device', 'C', value='10uF',
                 footprint='Capacitor_SMD:C_0603_1608Metric')
    
    # Create nets
    gnd = Net('GND')
    v3v3 = Net('3.3V')
    v5_mon = Net('5v_monitor')  # Net for 5V monitor output
    v3v3_mon = Net('3v3_monitor')  # Net for 3.3V monitor output
    
    # Connect power 
    c_in[1] += vin_5v  
    c_in[2] += gnd
    reg['VI'] += vin_5v
    reg['GND'] += gnd
    reg['VO'] += v3v3
    c_out[1] += v3v3
    c_out[2] += gnd
    
    # 5V monitor divider (2:1 ratio for 5V to ~2.5V)
    r5_top = Part('Device', 'R', value='2K',
                  footprint='Resistor_SMD:R_0603_1608Metric')
    r5_bot = Part('Device', 'R', value='1K',
                  footprint='Resistor_SMD:R_0603_1608Metric')
    
    r5_top[1] += vin_5v
    r5_top[2] += v5_mon
    r5_bot[1] += v5_mon
    r5_bot[2] += gnd

    # 3.3V monitor divider (2:1 ratio for 3.3V to ~1.65V)
    r3_top = Part('Device', 'R', value='2K',
                  footprint='Resistor_SMD:R_0603_1608Metric')
    r3_bot = Part('Device', 'R', value='1K',
                  footprint='Resistor_SMD:R_0603_1608Metric')
    
    r3_top[1] += v3v3
    r3_top[2] += v3v3_mon
    r3_bot[1] += v3v3_mon
    r3_bot[2] += gnd

    return v3v3, gnd, v5_mon, v3v3_mon

@subcircuit
def usb_circuit():
    """USB interface with Type-C connector"""
    usb = Part('Connector', 'USB_C_Plug_USB2.0',
               footprint='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
    
    # Create nets
    vbus = Net('VBUS')
    gnd = Net('GND')
    dp = Net('D+')
    dm = Net('D-')
    
    # Connect USB pins
    usb['A4,A9,B4,B9'] += vbus  # All VBUS pins
    usb['A1,A12,B1,B12,S1'] += gnd  # All GND pins including shield
    usb['A6'] += dp    # D+
    usb['A7'] += dm    # D-
    
    # CC pulldown resistor
    r_cc = Part('Device', 'R', value='5.1K',
                footprint='Resistor_SMD:R_0603_1608Metric')
    usb['A5'] += r_cc[1]  
    r_cc[2] += gnd
    
    return vbus, gnd, dp, dm

@subcircuit
def esp32_circuit(v3v3, gnd, v5_mon, v3v3_mon):
    """ESP32 microcontroller with programming header"""
    esp = Part('RF_Module', 'ESP32-S3-MINI-1',
               footprint='RF_Module:ESP32-S2-MINI-1')
    
    # Decoupling cap
    c_dec = Part('Device', 'C', value='100nF',
                 footprint='Capacitor_SMD:C_0603_1608Metric')
    c_dec[1] += v3v3  
    c_dec[2] += gnd
    
    # ESP32 power/ground connections
    esp[3] += v3v3  # 3V3 pin
    esp['1,2,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65'] += gnd
    
    # Programming header
    hdr = Part('Connector_Generic', 'Conn_02x03_Odd_Even',
               footprint='Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical')
    
    hdr[1] += esp[45]    # EN pin
    hdr[2] += v3v3       # 3.3V
    hdr[3] += esp[39]    # TXD0 pin
    hdr[4] += gnd        # GND
    hdr[5] += esp[4]     # IO0 pin
    hdr[6] += gnd        # GND
    
    # Hardware version divider
    r1 = Part('Device', 'R', value='2K',
              footprint='Resistor_SMD:R_0603_1608Metric')
    r2 = Part('Device', 'R', value='1K',
              footprint='Resistor_SMD:R_0603_1608Metric')
    hw_ver = Net('HW_VER')
    
    r1[1] += v3v3
    r1[2] += hw_ver 
    r2[1] += hw_ver
    r2[2] += gnd
    
    esp[5] += hw_ver  # IO1 pin

    # Connect voltage monitoring pins
    esp[6] += v5_mon   # IO2 - 5V monitor
    esp[7] += v3v3_mon # IO3 - 3.3V monitor

    return esp

def main():
    # Create 5V power net
    vdd5 = Net('VBUS')  # Changed to match USB VBUS
    vdd5.drive = POWER
    
    # Get USB interface nets
    usb_vbus, usb_gnd, usb_dp, usb_dm = usb_circuit()
    
    # Get regulated 3.3V and voltage monitoring nets
    v3v3, gnd, v5_mon, v3v3_mon = power_3v3_reg(usb_vbus)
    v3v3.drive = POWER
    
    # Connect grounds
    gnd += usb_gnd
    
    # Get ESP32 and connect all signals
    esp = esp32_circuit(v3v3, gnd, v5_mon, v3v3_mon)
    esp[23] += usb_dm  # IO19 for D-
    esp[24] += usb_dp  # IO20 for D+
    
    ERC()
    generate_netlist()

if __name__ == '__main__':
    main()