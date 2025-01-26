# -*- coding: utf-8 -*-

from skidl import *


def _Users_shanemattner_Desktop_skidl_kicad_schematic_parser_example_kicad_project_resistor_divider_kicad_sch():

    #===============================================================================
    # Component templates.
    #===============================================================================

    Device_C_Capacitor_SMD_C_0603_1608Metric = Part('Device', 'C', dest=TEMPLATE, footprint='Capacitor_SMD:C_0603_1608Metric')
    setattr(Device_C_Capacitor_SMD_C_0603_1608Metric, 'Footprint', 'Capacitor_SMD:C_0603_1608Metric')
    setattr(Device_C_Capacitor_SMD_C_0603_1608Metric, 'Datasheet', '')
    setattr(Device_C_Capacitor_SMD_C_0603_1608Metric, 'Description', 'Unpolarized capacitor')

    Device_R_Resistor_SMD_R_0603_1608Metric = Part('Device', 'R', dest=TEMPLATE, footprint='Resistor_SMD:R_0603_1608Metric')
    setattr(Device_R_Resistor_SMD_R_0603_1608Metric, 'Footprint', 'Resistor_SMD:R_0603_1608Metric')
    setattr(Device_R_Resistor_SMD_R_0603_1608Metric, 'Datasheet', '')
    setattr(Device_R_Resistor_SMD_R_0603_1608Metric, 'Description', 'Resistor')


    #===============================================================================
    # Component instantiations.
    #===============================================================================

    C10 = Device_C_Capacitor_SMD_C_0603_1608Metric(ref='C10', value='100nF')

    R10 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R10', value='1k')

    R9 = Device_R_Resistor_SMD_R_0603_1608Metric(ref='R9', value='2k')


    #===============================================================================
    # Net interconnections between instantiated components.
    #===============================================================================

    Net('/VIN').connect(R9['1'])

    Net('/VOUT').connect(C10['1'], R10['1'], R9['2'])

    Net('GND').connect(C10['2'], R10['2'])


#===============================================================================
# Instantiate the circuit and generate the netlist.
#===============================================================================

if __name__ == "__main__":
    _Users_shanemattner_Desktop_skidl_kicad_schematic_parser_example_kicad_project_resistor_divider_kicad_sch()
    generate_netlist()
