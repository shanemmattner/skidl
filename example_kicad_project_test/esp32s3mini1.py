# -*- coding: utf-8 -*-
from skidl import *
from resistor_divider1 import resistor_divider1

@subcircuit
def esp32s3mini1(3v3_monitor, 5v_monitor, d_, esp32s3mini1_hw_ver, gnd, net_3v3):
    # Local nets
    esp32s3mini1_en = Net('esp32s3mini1_en')
    esp32s3mini1_io0 = Net('esp32s3mini1_io0')
    esp32s3mini1_rx = Net('esp32s3mini1_rx')
    esp32s3mini1_tx = Net('esp32s3mini1_tx')
    unconnected__u3_io10_pad14_ = Net('unconnected__u3_io10_pad14_')
    unconnected__u3_io11_pad15_ = Net('unconnected__u3_io11_pad15_')
    unconnected__u3_io12_pad16_ = Net('unconnected__u3_io12_pad16_')
    unconnected__u3_io13_pad17_ = Net('unconnected__u3_io13_pad17_')
    unconnected__u3_io14_pad18_ = Net('unconnected__u3_io14_pad18_')
    unconnected__u3_io15_pad19_ = Net('unconnected__u3_io15_pad19_')
    unconnected__u3_io16_pad20_ = Net('unconnected__u3_io16_pad20_')
    unconnected__u3_io17_pad21_ = Net('unconnected__u3_io17_pad21_')
    unconnected__u3_io18_pad22_ = Net('unconnected__u3_io18_pad22_')
    unconnected__u3_io21_pad25_ = Net('unconnected__u3_io21_pad25_')
    unconnected__u3_io26_pad26_ = Net('unconnected__u3_io26_pad26_')
    unconnected__u3_io33_pad28_ = Net('unconnected__u3_io33_pad28_')
    unconnected__u3_io34_pad29_ = Net('unconnected__u3_io34_pad29_')
    unconnected__u3_io35_pad31_ = Net('unconnected__u3_io35_pad31_')
    unconnected__u3_io36_pad32_ = Net('unconnected__u3_io36_pad32_')
    unconnected__u3_io37_pad33_ = Net('unconnected__u3_io37_pad33_')
    unconnected__u3_io38_pad34_ = Net('unconnected__u3_io38_pad34_')
    unconnected__u3_io39_pad35_ = Net('unconnected__u3_io39_pad35_')
    unconnected__u3_io40_pad36_ = Net('unconnected__u3_io40_pad36_')
    unconnected__u3_io41_pad37_ = Net('unconnected__u3_io41_pad37_')
    unconnected__u3_io42_pad38_ = Net('unconnected__u3_io42_pad38_')
    unconnected__u3_io45_pad41_ = Net('unconnected__u3_io45_pad41_')
    unconnected__u3_io46_pad44_ = Net('unconnected__u3_io46_pad44_')
    unconnected__u3_io47_pad27_ = Net('unconnected__u3_io47_pad27_')
    unconnected__u3_io48_pad30_ = Net('unconnected__u3_io48_pad30_')
    unconnected__u3_io4_pad8_ = Net('unconnected__u3_io4_pad8_')
    unconnected__u3_io5_pad9_ = Net('unconnected__u3_io5_pad9_')
    unconnected__u3_io6_pad10_ = Net('unconnected__u3_io6_pad10_')
    unconnected__u3_io7_pad11_ = Net('unconnected__u3_io7_pad11_')
    unconnected__u3_io8_pad12_ = Net('unconnected__u3_io8_pad12_')
    unconnected__u3_io9_pad13_ = Net('unconnected__u3_io9_pad13_')

    # Components
    c1 = Part('Device', 'C', value='10uF', footprint='Capacitor_SMD:C_0603_1608Metric')
    j1 = Part('Connector_Generic', 'Conn_02x03_Odd_Even', value='Conn_02x03_Odd_Even', footprint='Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical')
    u3 = Part('RF_Module', 'ESP32-S3-MINI-1', value='ESP32-S3-MINI-1', footprint='RF_Module:ESP32-S2-MINI-1')

    # Connections
    net_3v3 += c1['1'], j1['2'], u3['3']
    3v3_monitor += u3['6']
    5v_monitor += u3['7']
    d_ += u3['24']
    d_ += u3['23']
    esp32s3mini1_en += j1['1'], u3['45']
    esp32s3mini1_hw_ver += u3['5']
    esp32s3mini1_io0 += j1['6'], u3['4']
    esp32s3mini1_rx += j1['5'], u3['40']
    esp32s3mini1_tx += j1['3'], u3['39']
    gnd += c1['2'], j1['4'], u3['1'], u3['2'], u3['42'], u3['43'], u3['46'], u3['47'], u3['48'], u3['49'], u3['50'], u3['51'], u3['52'], u3['53'], u3['54'], u3['55'], u3['56'], u3['57'], u3['58'], u3['59'], u3['60'], u3['61'], u3['62'], u3['63'], u3['64'], u3['65']
    unconnected__u3_io4_pad8_ += u3['8']
    unconnected__u3_io5_pad9_ += u3['9']
    unconnected__u3_io6_pad10_ += u3['10']
    unconnected__u3_io7_pad11_ += u3['11']
    unconnected__u3_io8_pad12_ += u3['12']
    unconnected__u3_io9_pad13_ += u3['13']
    unconnected__u3_io10_pad14_ += u3['14']
    unconnected__u3_io11_pad15_ += u3['15']
    unconnected__u3_io12_pad16_ += u3['16']
    unconnected__u3_io13_pad17_ += u3['17']
    unconnected__u3_io14_pad18_ += u3['18']
    unconnected__u3_io15_pad19_ += u3['19']
    unconnected__u3_io16_pad20_ += u3['20']
    unconnected__u3_io17_pad21_ += u3['21']
    unconnected__u3_io18_pad22_ += u3['22']
    unconnected__u3_io21_pad25_ += u3['25']
    unconnected__u3_io26_pad26_ += u3['26']
    unconnected__u3_io33_pad28_ += u3['28']
    unconnected__u3_io34_pad29_ += u3['29']
    unconnected__u3_io35_pad31_ += u3['31']
    unconnected__u3_io36_pad32_ += u3['32']
    unconnected__u3_io37_pad33_ += u3['33']
    unconnected__u3_io38_pad34_ += u3['34']
    unconnected__u3_io39_pad35_ += u3['35']
    unconnected__u3_io40_pad36_ += u3['36']
    unconnected__u3_io41_pad37_ += u3['37']
    unconnected__u3_io42_pad38_ += u3['38']
    unconnected__u3_io45_pad41_ += u3['41']
    unconnected__u3_io46_pad44_ += u3['44']
    unconnected__u3_io47_pad27_ += u3['27']
    unconnected__u3_io48_pad30_ += u3['30']
