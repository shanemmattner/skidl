from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

MCU_WCH_CH32V2 = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'CH32V203CxTx', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CH32V203CxTx'}), 'ref_prefix':'U', 'fplist':['Package_QFP:LQFP-48_7x7mm_P0.5mm'], 'footprint':'Package_QFP:LQFP-48_7x7mm_P0.5mm', 'keywords':'RISC-V WCH MCU', 'description':'', 'datasheet':'https://www.wch-ic.com/products/CH32V203.html', 'pins':[
            Pin(num='1',name='VBAT',func=Pin.types.PWRIN),
            Pin(num='23',name='VSS',func=Pin.types.PWRIN),
            Pin(num='24',name='VDD_VIO',func=Pin.types.PWRIN),
            Pin(num='44',name='BOOT0',func=Pin.types.INPUT),
            Pin(num='8',name='VSSA',func=Pin.types.PWRIN),
            Pin(num='9',name='VDDA',func=Pin.types.PWRIN),
            Pin(num='10',name='PA0',func=Pin.types.BIDIR,unit=1),
            Pin(num='11',name='PA1',func=Pin.types.BIDIR,unit=1),
            Pin(num='12',name='PA2',func=Pin.types.BIDIR,unit=1),
            Pin(num='13',name='PA3',func=Pin.types.BIDIR,unit=1),
            Pin(num='14',name='PA4',func=Pin.types.BIDIR,unit=1),
            Pin(num='15',name='PA5',func=Pin.types.BIDIR,unit=1),
            Pin(num='16',name='PA6',func=Pin.types.BIDIR,unit=1),
            Pin(num='17',name='PA7',func=Pin.types.BIDIR,unit=1),
            Pin(num='18',name='PB0',func=Pin.types.BIDIR,unit=1),
            Pin(num='19',name='PB1',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='PC13',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='PB2',func=Pin.types.BIDIR,unit=1),
            Pin(num='21',name='PB10',func=Pin.types.BIDIR,unit=1),
            Pin(num='22',name='PB11',func=Pin.types.BIDIR,unit=1),
            Pin(num='25',name='PB12',func=Pin.types.BIDIR,unit=1),
            Pin(num='26',name='PB13',func=Pin.types.BIDIR,unit=1),
            Pin(num='27',name='PB14',func=Pin.types.BIDIR,unit=1),
            Pin(num='28',name='PB15',func=Pin.types.BIDIR,unit=1),
            Pin(num='29',name='PA8',func=Pin.types.BIDIR,unit=1),
            Pin(num='3',name='PC14',func=Pin.types.BIDIR,unit=1),
            Pin(num='30',name='PA9',func=Pin.types.BIDIR,unit=1),
            Pin(num='31',name='PA10',func=Pin.types.BIDIR,unit=1),
            Pin(num='32',name='PA11',func=Pin.types.BIDIR,unit=1),
            Pin(num='33',name='PA12',func=Pin.types.BIDIR,unit=1),
            Pin(num='34',name='SWDIO',func=Pin.types.BIDIR,unit=1),
            Pin(num='35',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='36',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='37',name='SWCLK',func=Pin.types.BIDIR,unit=1),
            Pin(num='38',name='PA15',func=Pin.types.BIDIR,unit=1),
            Pin(num='39',name='PB3',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='PC15',func=Pin.types.BIDIR,unit=1),
            Pin(num='40',name='PB4',func=Pin.types.BIDIR,unit=1),
            Pin(num='41',name='PB5',func=Pin.types.BIDIR,unit=1),
            Pin(num='42',name='PB6',func=Pin.types.BIDIR,unit=1),
            Pin(num='43',name='PB7',func=Pin.types.BIDIR,unit=1),
            Pin(num='45',name='PB8',func=Pin.types.BIDIR,unit=1),
            Pin(num='46',name='PB9',func=Pin.types.BIDIR,unit=1),
            Pin(num='47',name='VSS',func=Pin.types.PASSIVE,unit=1),
            Pin(num='48',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='OSC_IN',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='OSC_OUT',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='~{RST}',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'CH32V203F6P6', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CH32V203F6P6'}), 'ref_prefix':'U', 'fplist':['Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'], 'footprint':'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm', 'keywords':'RISC-V WCH MCU', 'description':'', 'datasheet':'http://www.wch-ic.com/products/CH32V203.html', 'pins':[
            Pin(num='1',name='BOOT0',func=Pin.types.BIDIR,unit=1),
            Pin(num='10',name='PA4',func=Pin.types.BIDIR,unit=1),
            Pin(num='11',name='PA5',func=Pin.types.BIDIR,unit=1),
            Pin(num='12',name='PA6',func=Pin.types.BIDIR,unit=1),
            Pin(num='13',name='PA7',func=Pin.types.BIDIR,unit=1),
            Pin(num='14',name='PB1',func=Pin.types.BIDIR,unit=1),
            Pin(num='15',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='16',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='17',name='PA11',func=Pin.types.BIDIR,unit=1),
            Pin(num='18',name='PA12',func=Pin.types.BIDIR,unit=1),
            Pin(num='19',name='SWDIO',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='OSC_IN',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='SWCLK',func=Pin.types.BIDIR,unit=1),
            Pin(num='3',name='OSC_OUT',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='~{RST}',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDDA',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='PA0',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='PA1',func=Pin.types.BIDIR,unit=1),
            Pin(num='8',name='PA2',func=Pin.types.BIDIR,unit=1),
            Pin(num='9',name='PA3',func=Pin.types.BIDIR,unit=1)], 'unit_defs':[] })])