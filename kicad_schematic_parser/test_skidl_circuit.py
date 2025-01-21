from skidl import *

@subcircuit
def power_3v3_reg(vin_5v):
    """Power regulation with monitoring"""
    # Create regulator and caps
    reg = Part('Regulator_Linear', 'NCP1117-3.3_SOT223')
    c_in = Part('Device', 'C', value='10uF')
    c_out = Part('Device', 'C', value='10uF')
    
    # Create nets
    gnd = Net('GND')
    v3v3 = Net('3.3V')
    v5_mon = Net('5v_monitor')
    v3v3_mon = Net('3v3_monitor')
    
    # Connect power input caps
    c_in[1] += vin_5v  
    c_in[2] += gnd
    
    # Connect regulator
    reg['VI'] += vin_5v
    reg['GND'] += gnd
    reg['VO'] += v3v3
    
    # Connect output caps
    c_out[1] += v3v3
    c_out[2] += gnd
    
    # Voltage dividers for monitoring
    r5_1 = Part('Device', 'R', value='2K')
    r5_2 = Part('Device', 'R', value='1K')
    r3_1 = Part('Device', 'R', value='2K') 
    r3_2 = Part('Device', 'R', value='1K')
    
    # 5V monitor divider
    r5_1[1] += vin_5v
    r5_1[2] += v5_mon
    r5_2[1] += v5_mon
    r5_2[2] += gnd
    
    # 3.3V monitor divider
    r3_1[1] += v3v3
    r3_1[2] += v3v3_mon
    r3_2[1] += v3v3_mon
    r3_2[2] += gnd
    
    return v3v3, gnd, v5_mon, v3v3_mon

@subcircuit
def usb_circuit():
    """USB interface with Type-C connector"""
    usb = Part('Connector', 'USB_C_Plug_USB2.0')
    
    # Create nets
    vbus = Net('VBUS')
    gnd = Net('GND')
    dp = Net('D+')
    dm = Net('D-')
    
    # Connect USB pins
    usb['A4'] += vbus  # VBUS
    usb['A1'] += gnd   # GND
    usb['A6'] += dp    # D+
    usb['A7'] += dm    # D-
    
    # CC pulldown
    r_cc = Part('Device', 'R', value='5.1K')
    usb['A5'] += r_cc[1]  # CC1
    r_cc[2] += gnd
    
    return vbus, gnd, dp, dm

@subcircuit
def esp32_circuit(v3v3, gnd):
    """ESP32 microcontroller with programming header"""
    esp = Part('RF_Module', 'ESP32-S3-MINI-1')
    c_dec = Part('Device', 'C', value='100nF')
    
    # Power connections
    esp[3] += v3v3  # 3V3 pin
    esp[1] += gnd   # GND pin
    c_dec[1] += v3v3  
    c_dec[2] += gnd
    
    # Programming header
    hdr = Part('Connector_Generic', 'Conn_02x03_Odd_Even')
    
    # Connect header pins individually
    hdr[1] += esp[45]    # EN pin
    hdr[2] += v3v3       # 3.3V
    hdr[3] += esp[39]    # TXD0 pin
    hdr[4] += gnd        # GND
    hdr[5] += esp[4]     # IO0 pin
    hdr[6] += gnd        # GND
    
    # Hardware version divider
    r1 = Part('Device', 'R', value='2K')
    r2 = Part('Device', 'R', value='1K')
    hw_ver = Net('HW_VER')
    
    r1[1] += v3v3
    r1[2] += hw_ver
    r2[1] += hw_ver
    r2[2] += gnd
    
    esp[5] += hw_ver  # IO1 pin
    
    return esp

def main():
    # Create 5V power net
    vdd5 = Net('+5V')
    
    # Get USB interface nets
    usb_vbus, usb_gnd, usb_dp, usb_dm = usb_circuit()
    
    # Connect USB power to 5V rail
    vdd5 += usb_vbus
    
    # Get regulated 3.3V and grounds
    v3v3, gnd, v5_mon, v3v3_mon = power_3v3_reg(vdd5)
    
    # Connect grounds
    gnd += usb_gnd
    
    # Get ESP32 and connect USB data lines
    esp = esp32_circuit(v3v3, gnd)
    esp[23] += usb_dm  # IO19 for D-
    esp[24] += usb_dp  # IO20 for D+
    
    ERC()
    generate_netlist()

if __name__ == '__main__':
    main()