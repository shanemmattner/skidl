from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

main_lib = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':[''], 'footprint':'Capacitor_SMD:C_0603_1608Metric', 'keywords':'cap capacitor', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':[''], 'footprint':'Resistor_SMD:R_0603_1608Metric', 'keywords':'R res resistor', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='~',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Conn_02x03_Odd_Even', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Conn_02x03_Odd_Even'}), 'ref_prefix':'J', 'fplist':[''], 'footprint':'Connector_IDC:IDC-Header_2x03_P2.54mm_Vertical', 'keywords':'connector', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='Pin_1',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='Pin_2',func=pin_types.PASSIVE,unit=1),
            Pin(num='3',name='Pin_3',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='Pin_4',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='Pin_5',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='Pin_6',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'ESP32-S3-MINI-1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ESP32-S3-MINI-1'}), 'ref_prefix':'U', 'fplist':['RF_Module:ESP32-S2-MINI-1'], 'footprint':'RF_Module:ESP32-S2-MINI-1', 'keywords':'RF Radio BT ESP ESP32-S3 Espressif', 'description':'', 'datasheet':'https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='IO6',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='IO7',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='IO8',func=pin_types.BIDIR,unit=1),
            Pin(num='13',name='IO9',func=pin_types.BIDIR,unit=1),
            Pin(num='14',name='IO10',func=pin_types.BIDIR,unit=1),
            Pin(num='15',name='IO11',func=pin_types.BIDIR,unit=1),
            Pin(num='16',name='IO12',func=pin_types.BIDIR,unit=1),
            Pin(num='17',name='IO13',func=pin_types.BIDIR,unit=1),
            Pin(num='18',name='IO14',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='IO15',func=pin_types.BIDIR,unit=1),
            Pin(num='2',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='20',name='IO16',func=pin_types.BIDIR,unit=1),
            Pin(num='21',name='IO17',func=pin_types.BIDIR,unit=1),
            Pin(num='22',name='IO18',func=pin_types.BIDIR,unit=1),
            Pin(num='23',name='IO19',func=pin_types.BIDIR,unit=1),
            Pin(num='24',name='IO20',func=pin_types.BIDIR,unit=1),
            Pin(num='25',name='IO21',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='IO26',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='IO47',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='IO33',func=pin_types.BIDIR,unit=1),
            Pin(num='29',name='IO34',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='3V3',func=pin_types.PWRIN,unit=1),
            Pin(num='30',name='IO48',func=pin_types.BIDIR,unit=1),
            Pin(num='31',name='IO35',func=pin_types.BIDIR,unit=1),
            Pin(num='32',name='IO36',func=pin_types.BIDIR,unit=1),
            Pin(num='33',name='IO37',func=pin_types.BIDIR,unit=1),
            Pin(num='34',name='IO38',func=pin_types.BIDIR,unit=1),
            Pin(num='35',name='IO39',func=pin_types.BIDIR,unit=1),
            Pin(num='36',name='IO40',func=pin_types.BIDIR,unit=1),
            Pin(num='37',name='IO41',func=pin_types.BIDIR,unit=1),
            Pin(num='38',name='IO42',func=pin_types.BIDIR,unit=1),
            Pin(num='39',name='TXD0',func=pin_types.BIDIR,unit=1),
            Pin(num='4',name='IO0',func=pin_types.BIDIR,unit=1),
            Pin(num='40',name='RXD0',func=pin_types.BIDIR,unit=1),
            Pin(num='41',name='IO45',func=pin_types.BIDIR,unit=1),
            Pin(num='42',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='43',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='44',name='IO46',func=pin_types.BIDIR,unit=1),
            Pin(num='45',name='EN',func=pin_types.INPUT,unit=1),
            Pin(num='46',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='47',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='48',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='49',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='5',name='IO1',func=pin_types.BIDIR,unit=1),
            Pin(num='50',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='51',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='52',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='53',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='54',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='55',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='56',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='57',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='58',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='59',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='6',name='IO2',func=pin_types.BIDIR,unit=1),
            Pin(num='60',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='61',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='62',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='63',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='64',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='65',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='7',name='IO3',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='IO4',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='IO5',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'NCP1117-3.3_SOT223', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'NCP1117-3.3_SOT223'}), 'ref_prefix':'U', 'fplist':['Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'], 'footprint':'Package_TO_SOT_SMD:SOT-223-3_TabPin2', 'keywords':'REGULATOR LDO 3.3V', 'description':'', 'datasheet':'http://www.onsemi.com/pub_link/Collateral/NCP1117-D.PDF', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='2',name='VO',func=pin_types.PWROUT,unit=1),
            Pin(num='3',name='VI',func=pin_types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'USB_C_Plug_USB2.0', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'USB_C_Plug_USB2.0'}), 'ref_prefix':'P', 'fplist':[''], 'footprint':'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal', 'keywords':'usb universal serial bus type-C USB2.0', 'description':'', 'datasheet':'https://www.usb.org/sites/default/files/documents/usb_type-c.zip', 'pins':[
            Pin(num='A1',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='A12',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='A4',name='VBUS',func=pin_types.PASSIVE,unit=1),
            Pin(num='A5',name='CC',func=pin_types.BIDIR,unit=1),
            Pin(num='A6',name='D+',func=pin_types.BIDIR,unit=1),
            Pin(num='A7',name='D-',func=pin_types.BIDIR,unit=1),
            Pin(num='A9',name='VBUS',func=pin_types.PASSIVE,unit=1),
            Pin(num='B1',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='B12',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='B4',name='VBUS',func=pin_types.PASSIVE,unit=1),
            Pin(num='B5',name='VCONN',func=pin_types.BIDIR,unit=1),
            Pin(num='B9',name='VBUS',func=pin_types.PASSIVE,unit=1),
            Pin(num='S1',name='SHIELD',func=pin_types.PASSIVE,unit=1)], 'unit_defs':[] })])