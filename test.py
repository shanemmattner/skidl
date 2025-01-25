# -*- coding: utf-8 -*-

from skidl import *


def _Users_shanemattner_Desktop_skidl_kicad_schematic_parser_example_kicad_project_example_kicad_project_kicad_sch():

    #===============================================================================
    # Component templates.
    #===============================================================================

    Connector_Generic_Conn_02x03_Odd_Even_Connector_IDC_IDC_Header_2x03_P2_54mm_Vertical = Part('Connector_Generic', 'Conn_02x03_Odd_Even', dest=TEMPLATE, footprint='Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical')
    setattr(Connector_Generic_Conn_02x03_Odd_Even_Connector_IDC_IDC_Header_2x03_P2_54mm_Vertical, 'Footprint', 'Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical')
    setattr(Connector_Generic_Conn_02x03_Odd_Even_Connector_IDC_IDC_Header_2x03_P2_54mm_Vertical, 'Datasheet', '')
    setattr(Connector_Generic_Conn_02x03_Odd_Even_Connector_IDC_IDC_Header_2x03_P2_54mm_Vertical, 'Description', 'Generic connector, double row, 02x03, odd/even pin numbering scheme (row 1 odd numbers, row 2 even numbers), script generated (kicad-library-utils/schlib/autogen/connector/)')

    Connector_USB_C_Plug_USB2_0_Connector_USB_USB_C_Receptacle_GCT_USB4105_xx_A_16P_TopMnt_Horizontal = Part('Connector', 'USB_C_Plug_USB2.0', dest=TEMPLATE, footprint='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
    setattr(Connector_USB_C_Plug_USB2_0_Connector_USB_USB_C_Receptacle_GCT_USB4105_xx_A_16P_TopMnt_Horizontal, 'Footprint', 'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
    setattr(Connector_USB_C_Plug_USB2_0_Connector_USB_USB_C_Receptacle_GCT_USB4105_xx_A_16P_TopMnt_Horizontal, 'Datasheet', 'https://www.usb.org/sites/default/files/documents/usb_type-c.zip')
    setattr(Connector_USB_C_Plug_USB2_0_Connector_USB_USB_C_Receptacle_GCT_USB4105_xx_A_16P_TopMnt_Horizontal, 'Description', 'USB 2.0-only Type-C Plug connector')

    Device_C = Part('Device', 'C', dest=TEMPLATE)
    setattr(Device_C, 'Footprint', '')
    setattr(Device_C, 'Datasheet', '')
    setattr(Device_C, 'Description', 'Unpolarized capacitor')

    Device_C_Capacitor_SMD_C_0603_1608Metric = Part('Device', 'C', dest=TEMPLATE, footprint='Capacitor_SMD:C_0603_1608Metric')
    setattr(Device_C_Capacitor_SMD_C_0603_1608Metric, 'Footprint', 'Capacitor_SMD:C_0603_1608Metric')
    setattr(Device_C_Capacitor_SMD_C_0603_1608Metric, 'Datasheet', '')
    setattr(Device_C_Capacitor_SMD_C_0603_1608Metric, 'Description', 'Unpolarized capacitor')

    Device_R_Resistor_SMD_R_0603_1608Metric = Part('Device', 'R', dest=TEMPLATE, footprint='Resistor_SMD:R_0603_1608Metric')
    setattr(Device_R_Resistor_SMD_R_0603_1608Metric, 'Footprint', 'Resistor_SMD:R_0603_1608Metric')
    setattr(Device_R_Resistor_SMD_R_0603_1608Metric, 'Datasheet', '')
    setattr(Device_R_Resistor_SMD_R_0603_1608Metric, 'Description', 'Resistor')

    RF_Module_ESP32_S3_MINI_1_RF_Module_ESP32_S2_MINI_1 = Part('RF_Module', 'ESP32-S3-MINI-1', dest=TEMPLATE, footprint='RF_Module:ESP32-S2-MINI-1')
    setattr(RF_Module_ESP32_S3_MINI_1_RF_Module_ESP32_S2_MINI_1, 'Footprint', 'RF_Module:ESP32-S2-MINI-1')
    setattr(RF_Module_ESP32_S3_MINI_1_RF_Module_ESP32_S2_MINI_1, 'Datasheet', 'https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf')
    setattr(RF_Module_ESP32_S3_MINI_1_RF_Module_ESP32_S2_MINI_1, 'Description', 'RF Module, ESP32-S3 SoC, Wi-Fi 802.11b/g/n, Bluetooth, BLE, 32-bit, 3.3V, SMD, onboard antenna')

    Regulator_Linear_NCP1117_3_3_SOT223_Package_TO_SOT_SMD_SOT_223_3_TabPin2 = Part('Regulator_Linear', 'NCP1117-3.3_SOT223', dest=TEMPLATE, footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    setattr(Regulator_Linear_NCP1117_3_3_SOT223_Package_TO_SOT_SMD_SOT_223_3_TabPin2, 'Footprint', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2')
    setattr(Regulator_Linear_NCP1117_3_3_SOT223_Package_TO_SOT_SMD_SOT_223_3_TabPin2, 'Datasheet', 'http://www.onsemi.com/pub_link/Collateral/NCP1117-D.PDF')
    setattr(Regulator_Linear_NCP1117_3_3_SOT223_Package_TO_SOT_SMD_SOT_223_3_TabPin2, 'Description', '1A Low drop-out regulator, Fixed Output 3.3V, SOT-223')


    #===============================================================================
    # Component instantiations.
    #===============================================================================

    C1 = Device_C_Capacitor_SMD_C_0603_1608Metric(ref='C1', value='C')

    C10 = Device_C(ref='C10', value='100nF')

    C11 = Device_C(ref='C11', value='C')

    C2 = Device_C_Capacitor_SMD_C_0603_1608Metric(ref='C2', value='10uF')

    C3 = Device_C_Capacitor_SMD_C_0603_1608Metric(ref='C3', value='10uF')

    C4 = Device_C(ref='C4', value='10uF')

    C9 = Device_C(ref='C9', value='C')

    J1 = Connector_Generic_Conn_02x03_Odd_Even_Connector_IDC_IDC_Header_2x03_P2_54mm_Vertical(ref='J1', value='Conn_02x03_Odd_Even')

    P1 = Connector_USB_C_Plug_USB2_0_Connector_USB_USB_C_Receptacle_GCT_USB4105_xx_A_16P_TopMnt_Horizontal(ref='P1', value='USB_C_Plug_USB2.0')

    R1 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R1', value='5.1K')

    R10 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R10', value='1k')

    R11 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R11', value='R')

    R2 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R2', value='R')

    R7 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R7', value='R')

    R8 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R8', value='R')

    R9 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R9', value='2k')

    U1 = Regulator_Linear_NCP1117_3_3_SOT223_Package_TO_SOT_SMD_SOT_223_3_TabPin2(ref='U1', value='NCP1117-3.3_SOT223')

    U3 = RF_Module_ESP32_S3_MINI_1_RF_Module_ESP32_S2_MINI_1(ref='U3', value='ESP32-S3-MINI-1')


    #===============================================================================
    # Net interconnections between instantiated components.
    #===============================================================================

    Net('+3V3').connect(C1['1'], C2['1'], J1['2'], R8['1'], R9['1'], U1['2'], U3['3'])

    Net('+5V').connect(C3['1'], C4['1'], P1['A4'], P1['A9'], P1['B4'], P1['B9'], R2['1'], U1['3'])

    Net('/3v3_monitor').connect(C11['1'], R11['1'], R8['2'], U3['6'])

    Net('/5v_monitor').connect(C9['1'], R2['2'], R7['1'], U3['7'])

    Net('/D+').connect(P1['A6'], U3['24'])

    Net('/D-').connect(P1['A7'], U3['23'])

    Net('/esp32s3mini1/EN').connect(J1['1'], U3['45'])

    Net('/esp32s3mini1/HW_VER').connect(C10['1'], R10['1'], R9['2'], U3['5'])

    Net('/esp32s3mini1/IO0').connect(J1['6'], U3['4'])

    Net('/esp32s3mini1/RX').connect(J1['5'], U3['40'])

    Net('/esp32s3mini1/TX').connect(J1['3'], U3['39'])

    Net('GND').connect(C1['2'], C10['2'], C11['2'], C2['2'], C3['2'], C4['2'], C9['2'], J1['4'], P1['A1'], P1['A12'], P1['B1'], P1['B12'], P1['S1'], R1['2'], R10['2'], R11['2'], R7['2'], U1['1'], U3['1'], U3['2'], U3['42'], U3['43'], U3['46'], U3['47'], U3['48'], U3['49'], U3['50'], U3['51'], U3['52'], U3['53'], U3['54'], U3['55'], U3['56'], U3['57'], U3['58'], U3['59'], U3['60'], U3['61'], U3['62'], U3['63'], U3['64'], U3['65'])

    Net('Net-(P1-CC)').connect(P1['A5'], R1['1'])

    Net('unconnected-(P1-VCONN-PadB5)').connect(P1['B5'])

    Net('unconnected-(U3-IO10-Pad14)').connect(U3['14'])

    Net('unconnected-(U3-IO11-Pad15)').connect(U3['15'])

    Net('unconnected-(U3-IO12-Pad16)').connect(U3['16'])

    Net('unconnected-(U3-IO13-Pad17)').connect(U3['17'])

    Net('unconnected-(U3-IO14-Pad18)').connect(U3['18'])

    Net('unconnected-(U3-IO15-Pad19)').connect(U3['19'])

    Net('unconnected-(U3-IO16-Pad20)').connect(U3['20'])

    Net('unconnected-(U3-IO17-Pad21)').connect(U3['21'])

    Net('unconnected-(U3-IO18-Pad22)').connect(U3['22'])

    Net('unconnected-(U3-IO21-Pad25)').connect(U3['25'])

    Net('unconnected-(U3-IO26-Pad26)').connect(U3['26'])

    Net('unconnected-(U3-IO33-Pad28)').connect(U3['28'])

    Net('unconnected-(U3-IO34-Pad29)').connect(U3['29'])

    Net('unconnected-(U3-IO35-Pad31)').connect(U3['31'])

    Net('unconnected-(U3-IO36-Pad32)').connect(U3['32'])

    Net('unconnected-(U3-IO37-Pad33)').connect(U3['33'])

    Net('unconnected-(U3-IO38-Pad34)').connect(U3['34'])

    Net('unconnected-(U3-IO39-Pad35)').connect(U3['35'])

    Net('unconnected-(U3-IO4-Pad8)').connect(U3['8'])

    Net('unconnected-(U3-IO40-Pad36)').connect(U3['36'])

    Net('unconnected-(U3-IO41-Pad37)').connect(U3['37'])

    Net('unconnected-(U3-IO42-Pad38)').connect(U3['38'])

    Net('unconnected-(U3-IO45-Pad41)').connect(U3['41'])

    Net('unconnected-(U3-IO46-Pad44)').connect(U3['44'])

    Net('unconnected-(U3-IO47-Pad27)').connect(U3['27'])

    Net('unconnected-(U3-IO48-Pad30)').connect(U3['30'])

    Net('unconnected-(U3-IO5-Pad9)').connect(U3['9'])

    Net('unconnected-(U3-IO6-Pad10)').connect(U3['10'])

    Net('unconnected-(U3-IO7-Pad11)').connect(U3['11'])

    Net('unconnected-(U3-IO8-Pad12)').connect(U3['12'])

    Net('unconnected-(U3-IO9-Pad13)').connect(U3['13'])


#===============================================================================
# Instantiate the circuit and generate the netlist.
#===============================================================================

if __name__ == "__main__":
    _Users_shanemattner_Desktop_skidl_kicad_schematic_parser_example_kicad_project_example_kicad_project_kicad_sch()
    generate_netlist()
