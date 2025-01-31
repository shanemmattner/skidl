from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

RF_ZigBee = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'CC2520', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CC2520'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm'], 'footprint':'Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm', 'keywords':'2.4GHz rf transceiver ZigBee 802.15.4', 'description':'', 'datasheet':'http://www.ti.com/lit/gpn/cc2520', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nCC2520\n\n2.4GHz rf transceiver ZigBee 802.15.4', 'pins':[
            Pin(num='1',name='SO',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',name='GPIO0',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='AVDD5',func=pin_types.PWRIN,unit=1),
            Pin(num='12',name='XOSC_Q2',func=pin_types.PASSIVE,unit=1),
            Pin(num='13',name='XOSC_Q1',func=pin_types.PASSIVE,unit=1),
            Pin(num='14',name='AVDD3',func=pin_types.PWRIN,unit=1),
            Pin(num='15',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='16',name='AVDD2',func=pin_types.PWRIN,unit=1),
            Pin(num='17',name='RF_P',func=pin_types.PASSIVE,unit=1),
            Pin(num='19',name='RF_N',func=pin_types.PASSIVE,unit=1),
            Pin(num='2',name='SI',func=pin_types.INPUT,unit=1),
            Pin(num='20',name='AVDD1',func=pin_types.PWRIN,unit=1),
            Pin(num='21',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='22',name='AVDD4',func=pin_types.PWRIN,unit=1),
            Pin(num='23',name='RBIAS',func=pin_types.PASSIVE,unit=1),
            Pin(num='24',name='AVDD_GUARD',func=pin_types.PWRIN,unit=1),
            Pin(num='25',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='26',name='VREG_EN',func=pin_types.INPUT,unit=1),
            Pin(num='27',name='DCOUPL',func=pin_types.PASSIVE,unit=1),
            Pin(num='28',name='SCLK',func=pin_types.INPUT,unit=1),
            Pin(num='29',name='AGND',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='~{CS}',func=pin_types.INPUT,unit=1),
            Pin(num='4',name='GPIO5',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='GPIO4',func=pin_types.BIDIR,unit=1),
            Pin(num='6',name='GPIO3',func=pin_types.BIDIR,unit=1),
            Pin(num='7',name='GPIO2',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='DVDD',func=pin_types.PWRIN,unit=1),
            Pin(num='9',name='GPIO1',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MC13192', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC13192'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'ZIGBEE', 'description':'', 'datasheet':'https://www.nxp.com/products/no-longer-manufactured/2.4-ghz-low-power-transceiver-for-802.15.4:MC13192', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nMC13192\n\nZIGBEE', 'pins':[
            Pin(num='1',name='RFIN-',func=pin_types.INPUT,unit=1),
            Pin(num='10',name='GPIO2',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='GPIO1',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='RSTBi',func=pin_types.INPUT,unit=1),
            Pin(num='13',name='RXTXENi',func=pin_types.INPUT,unit=1),
            Pin(num='14',name='ATTNBi',func=pin_types.INPUT,unit=1),
            Pin(num='15',name='CLKOo',func=pin_types.OUTPUT,unit=1),
            Pin(num='16',name='SPICLKi',func=pin_types.INPUT,unit=1),
            Pin(num='17',name='MOSIi',func=pin_types.INPUT,unit=1),
            Pin(num='18',name='MISOo',func=pin_types.TRISTATE,unit=1),
            Pin(num='19',name='CEBi',func=pin_types.INPUT,unit=1),
            Pin(num='2',name='RFIN+',func=pin_types.INPUT,unit=1),
            Pin(num='20',name='IRQBo',func=pin_types.OPENCOLL,unit=1),
            Pin(num='21',name='VDDD',func=pin_types.PWROUT,unit=1),
            Pin(num='22',name='VDDIN',func=pin_types.PWRIN,unit=1),
            Pin(num='23',name='GPIO5',func=pin_types.BIDIR,unit=1),
            Pin(num='24',name='GPIO6',func=pin_types.BIDIR,unit=1),
            Pin(num='25',name='GPIO7',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='XTALin',func=pin_types.INPUT,unit=1),
            Pin(num='27',name='XTALout',func=pin_types.OUTPUT,unit=1),
            Pin(num='28',name='VDDLO2',func=pin_types.PWRIN,unit=1),
            Pin(num='29',name='VDDLO1',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='TINJ_P',func=pin_types.INPUT,unit=1),
            Pin(num='30',name='VDDVCO',func=pin_types.PWROUT,unit=1),
            Pin(num='31',name='VBATT',func=pin_types.INPUT,unit=1),
            Pin(num='32',name='VDDA',func=pin_types.PWROUT,unit=1),
            Pin(num='33',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='4',name='TINJ_M',func=pin_types.INPUT,unit=1),
            Pin(num='5',name='PAO_P',func=pin_types.OPENCOLL,unit=1),
            Pin(num='6',name='PAO_M',func=pin_types.OPENCOLL,unit=1),
            Pin(num='7',name='SM',func=pin_types.INPUT,unit=1),
            Pin(num='8',name='GPIO4',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='GPIO3',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TWE-L-DP-W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TWE-L-DP-W'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-28_W15.24mm'], 'footprint':'Package_DIP:DIP-28_W15.24mm', 'keywords':'TWELITE', 'description':'', 'datasheet':'https://www.mono-wireless.com/jp/products/TWE-Lite-DIP/MW-PDS-TWELITEDIP-JP.pdf', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nTWE-L-DP-W\n\nTWELITE', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='DIO6/TX',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='DIO8/PWM4',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='DIO9/DO4',func=pin_types.BIDIR,unit=1),
            Pin(num='13',name='DIO10/M1',func=pin_types.BIDIR,unit=1),
            Pin(num='14',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='DIO12/DI1',func=pin_types.BIDIR,unit=1),
            Pin(num='16',name='DIO13/DI2',func=pin_types.BIDIR,unit=1),
            Pin(num='17',name='DIO11/DI3',func=pin_types.BIDIR,unit=1),
            Pin(num='18',name='DIO16/DI4',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='DIO15/SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='2',name='DIO14/SCL',func=pin_types.BIDIR,unit=1),
            Pin(num='20',name='DIO17/BPS',func=pin_types.BIDIR,unit=1),
            Pin(num='21',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='ADC1/AI1',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='DIO0/AI2',func=pin_types.BIDIR,unit=1),
            Pin(num='24',name='ADC2/AI3',func=pin_types.INPUT,unit=1),
            Pin(num='25',name='DIO1/AI4',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='DIO2/M2',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='DIO3/M3',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='DIO7/RX',func=pin_types.BIDIR,unit=1),
            Pin(num='4',name='DIO5/PWM1',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='DIO18/DO1',func=pin_types.BIDIR,unit=1),
            Pin(num='6',name='DO0/PWM2',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='DO1/PWM3',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='DIO19/DO2',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='DIO4/DO3',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TWE-L-WX', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TWE-L-WX'}), 'ref_prefix':'U', 'fplist':['RF_Module:MonoWireless_TWE-L-WX'], 'footprint':'RF_Module:MonoWireless_TWE-L-WX', 'keywords':'TWELITE', 'description':'', 'datasheet':'https://www.mono-wireless.com/jp/products/TWE-LITE/MW-PDS-TWELITE-JP.pdf', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nTWE-L-WX\n\nTWELITE', 'pins':[
            Pin(num='1',name='DO0/PWM2',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',name='DIO8/PWM4',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='DIO9/DO4',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='DIO10/M1',func=pin_types.BIDIR,unit=1),
            Pin(num='13',name='DIO12/DI1',func=pin_types.BIDIR,unit=1),
            Pin(num='14',name='DIO14/SCL',func=pin_types.BIDIR,unit=1),
            Pin(num='15',name='DIO13/DI2',func=pin_types.BIDIR,unit=1),
            Pin(num='16',name='DIO11/DI3',func=pin_types.BIDIR,unit=1),
            Pin(num='17',name='DIO15/SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='18',name='DIO16/DI4',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='DIO17/BPS',func=pin_types.BIDIR,unit=1),
            Pin(num='2',name='DO1/PWM3',func=pin_types.BIDIR,unit=1),
            Pin(num='20',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='21',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='ADC2/AI3',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='ADC1/AI1',func=pin_types.INPUT,unit=1),
            Pin(num='24',name='DIO0/AI2',func=pin_types.BIDIR,unit=1),
            Pin(num='25',name='DIO1/AI4',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='DIO2/M2',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='DIO3/M3',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='29',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='DIO18/DO1',func=pin_types.BIDIR,unit=1),
            Pin(num='30',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='31',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='32',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='DIO19/DO2',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='DIO4/DO3',func=pin_types.BIDIR,unit=1),
            Pin(num='7',name='DIO5/PWM1',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='DIO6/TX',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='DIO7/RX',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'XBee_SMT', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'XBee_SMT'}), 'ref_prefix':'U', 'fplist':['RF_Module:Digi_XBee_SMT'], 'footprint':'RF_Module:Digi_XBee_SMT', 'keywords':'Digi XBee', 'description':'', 'datasheet':'http://www.digi.com/resources/documentation/digidocs/pdfs/90002126.pdf', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nXBee_SMT\n\nDigi XBee', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='DIO8/SLEEP_REQUEST',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='12',name='DIO19/SPI_~{ATTN}',func=pin_types.OUTPUT,unit=1),
            Pin(num='13',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='14',name='DIO18/SPI_CLK',func=pin_types.INPUT,unit=1),
            Pin(num='15',name='DIO17/SPI_~{SSEL}',func=pin_types.INPUT,unit=1),
            Pin(num='16',name='DIO16/SPI_MOSI',func=pin_types.INPUT,unit=1),
            Pin(num='17',name='DIO15/SPI_MISO',func=pin_types.OUTPUT,unit=1),
            Pin(num='18',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='19',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='2',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='20',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='21',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='22',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='23',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='24',name='DIO4',func=pin_types.BIDIR,unit=1),
            Pin(num='25',name='DIO7/~{CTS}',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='DIO9/ON/~{SLEEP}',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='VREF',func=pin_types.INPUT,unit=1),
            Pin(num='28',name='DIO5/ASSOCIATE',func=pin_types.BIDIR,unit=1),
            Pin(num='29',name='DIO6/~{RTS}',func=pin_types.BIDIR,unit=1),
            Pin(num='3',name='DIO13/UART_TX',func=pin_types.BIDIR,unit=1),
            Pin(num='30',name='DIO3/AD3',func=pin_types.BIDIR,unit=1),
            Pin(num='31',name='DIO2/AD2',func=pin_types.BIDIR,unit=1),
            Pin(num='32',name='DIO1/AD1',func=pin_types.BIDIR,unit=1),
            Pin(num='33',name='DIO0/AD0',func=pin_types.BIDIR,unit=1),
            Pin(num='34',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='35',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='36',name='RF',func=pin_types.BIDIR,unit=1),
            Pin(num='37',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='4',name='DIO14/UART_RX/~{CONFIG}',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='DIO12',func=pin_types.BIDIR,unit=1),
            Pin(num='6',name='RESET/OD_OUT',func=pin_types.BIDIR,unit=1),
            Pin(num='7',name='DIO10/RSSI/PWM0',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='DIO11/PWM1',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='NC',func=pin_types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MW-R-DP-W', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MW-R-DP-W'}), 'ref_prefix':'U', 'fplist':['Package_DIP:DIP-28_W15.24mm', 'Package_DIP:DIP-28_W15.24mm'], 'footprint':'Package_DIP:DIP-28_W15.24mm', 'keywords':'TWELITE', 'description':'', 'datasheet':'https://www.mono-wireless.com/jp/products/TWE-Lite-DIP/MW-PDS-TWELITEDIP-JP.pdf', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nMW-R-DP-W\n\nTWELITE', 'pins':[
            Pin(num='1',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='10',name='DIO6/TX',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='DIO8/PWM4',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='DIO9/DO4',func=pin_types.BIDIR,unit=1),
            Pin(num='13',name='DIO10/M1',func=pin_types.BIDIR,unit=1),
            Pin(num='14',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='15',name='DIO12/DI1',func=pin_types.BIDIR,unit=1),
            Pin(num='16',name='DIO13/DI2',func=pin_types.BIDIR,unit=1),
            Pin(num='17',name='DIO11/DI3',func=pin_types.BIDIR,unit=1),
            Pin(num='18',name='DIO16/DI4',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='DIO15/SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='2',name='DIO14/SCL',func=pin_types.BIDIR,unit=1),
            Pin(num='20',name='DIO17/BPS',func=pin_types.BIDIR,unit=1),
            Pin(num='21',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='ADC1/AI1',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='DIO0/AI2',func=pin_types.BIDIR,unit=1),
            Pin(num='24',name='ADC2/AI3',func=pin_types.INPUT,unit=1),
            Pin(num='25',name='DIO1/AI4',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='DIO2/M2',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='DIO3/M3',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='3',name='DIO7/RX',func=pin_types.BIDIR,unit=1),
            Pin(num='4',name='DIO5/PWM1',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='DIO18/DO1',func=pin_types.BIDIR,unit=1),
            Pin(num='6',name='DO0/PWM2',func=pin_types.OUTPUT,unit=1),
            Pin(num='7',name='DO1/PWM3',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='DIO19/DO2',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='DIO4/DO3',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MW-R-WX', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MW-R-WX'}), 'ref_prefix':'U', 'fplist':['RF_Module:MonoWireless_TWE-L-WX', 'RF_Module:MonoWireless_TWE-L-WX'], 'footprint':'RF_Module:MonoWireless_TWE-L-WX', 'keywords':'TWELITE', 'description':'', 'datasheet':'https://www.mono-wireless.com/jp/products/TWE-LITE/MW-PDS-TWELITE-JP.pdf', 'search_text':'/usr/share/kicad/symbols/RF_ZigBee.kicad_sym\nMW-R-WX\n\nTWELITE', 'pins':[
            Pin(num='1',name='DO0/PWM2',func=pin_types.OUTPUT,unit=1),
            Pin(num='10',name='DIO8/PWM4',func=pin_types.BIDIR,unit=1),
            Pin(num='11',name='DIO9/DO4',func=pin_types.BIDIR,unit=1),
            Pin(num='12',name='DIO10/M1',func=pin_types.BIDIR,unit=1),
            Pin(num='13',name='DIO12/DI1',func=pin_types.BIDIR,unit=1),
            Pin(num='14',name='DIO14/SCL',func=pin_types.BIDIR,unit=1),
            Pin(num='15',name='DIO13/DI2',func=pin_types.BIDIR,unit=1),
            Pin(num='16',name='DIO11/DI3',func=pin_types.BIDIR,unit=1),
            Pin(num='17',name='DIO15/SDA',func=pin_types.BIDIR,unit=1),
            Pin(num='18',name='DIO16/DI4',func=pin_types.BIDIR,unit=1),
            Pin(num='19',name='DIO17/BPS',func=pin_types.BIDIR,unit=1),
            Pin(num='2',name='DO1/PWM3',func=pin_types.BIDIR,unit=1),
            Pin(num='20',name='GND',func=pin_types.PWRIN,unit=1),
            Pin(num='21',name='~{RESET}',func=pin_types.INPUT,unit=1),
            Pin(num='22',name='ADC2/AI3',func=pin_types.INPUT,unit=1),
            Pin(num='23',name='ADC1/AI1',func=pin_types.INPUT,unit=1),
            Pin(num='24',name='DIO0/AI2',func=pin_types.BIDIR,unit=1),
            Pin(num='25',name='DIO1/AI4',func=pin_types.BIDIR,unit=1),
            Pin(num='26',name='DIO2/M2',func=pin_types.BIDIR,unit=1),
            Pin(num='27',name='DIO3/M3',func=pin_types.BIDIR,unit=1),
            Pin(num='28',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='29',name='NC',func=pin_types.NOCONNECT,unit=1),
            Pin(num='3',name='DIO18/DO1',func=pin_types.BIDIR,unit=1),
            Pin(num='30',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='31',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='32',name='GND',func=pin_types.PASSIVE,unit=1),
            Pin(num='4',name='DIO19/DO2',func=pin_types.BIDIR,unit=1),
            Pin(num='5',name='VCC',func=pin_types.PWRIN,unit=1),
            Pin(num='6',name='DIO4/DO3',func=pin_types.BIDIR,unit=1),
            Pin(num='7',name='DIO5/PWM1',func=pin_types.BIDIR,unit=1),
            Pin(num='8',name='DIO6/TX',func=pin_types.BIDIR,unit=1),
            Pin(num='9',name='DIO7/RX',func=pin_types.BIDIR,unit=1)], 'unit_defs':[] })])