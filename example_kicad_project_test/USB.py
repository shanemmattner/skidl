# -*- coding: utf-8 -*-
from skidl import *

@subcircuit
def USB(d_, gnd, net_5v):
    # Local nets
    net__p1_cc_ = Net('net__p1_cc_')
    unconnected__p1_vconn_padb5_ = Net('unconnected__p1_vconn_padb5_')

    # Components
    c4 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    p1 = Part('Connector', 'USB_C_Plug_USB2.0', value='USB_C_Plug_USB2.0', footprint='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
    r1 = Part('Device', 'R', value='5.1K', footprint='Resistor_SMD:R_0603_1608Metric')

    # Connections
    net_5v += c4['1'], p1['A4'], p1['A9'], p1['B4'], p1['B9']
    d_ += p1['A6']
    d_ += p1['A7']
    gnd += c4['2'], p1['A1'], p1['A12'], p1['B1'], p1['B12'], p1['S1'], r1['2']
    net__p1_cc_ += p1['A5'], r1['1']
    unconnected__p1_vconn_padb5_ += p1['B5']
