from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

CPU_NXP_68000 = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'68000D', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'68000D'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'68000 Microprocessor CPU', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/reference-manual/MC68000UM.pdf', 'pins':[
            Pin(num='1',name='D4',func=Pin.types.BIDIR,unit=1),
            Pin(num='10',name='DTACK',func=Pin.types.INPUT,unit=1),
            Pin(num='11',name='BG',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='BGACK',func=Pin.types.INPUT,unit=1),
            Pin(num='13',name='BR',func=Pin.types.INPUT,unit=1),
            Pin(num='14',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='15',name='CLK',func=Pin.types.INPUT,unit=1),
            Pin(num='16',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='17',name='HALT',func=Pin.types.BIDIR,unit=1),
            Pin(num='18',name='RESET',func=Pin.types.BIDIR,unit=1),
            Pin(num='19',name='VMA',func=Pin.types.OUTPUT,unit=1),
            Pin(num='2',name='D3',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='E',func=Pin.types.OUTPUT,unit=1),
            Pin(num='21',name='VPA',func=Pin.types.INPUT,unit=1),
            Pin(num='22',name='BERR',func=Pin.types.INPUT,unit=1),
            Pin(num='23',name='IPL2',func=Pin.types.INPUT,unit=1),
            Pin(num='24',name='IPL1',func=Pin.types.INPUT,unit=1),
            Pin(num='25',name='IPL0',func=Pin.types.INPUT,unit=1),
            Pin(num='26',name='FC2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='27',name='FC1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='28',name='FC0',func=Pin.types.OUTPUT,unit=1),
            Pin(num='29',name='A1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='3',name='D2',func=Pin.types.BIDIR,unit=1),
            Pin(num='30',name='A2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='31',name='A3',func=Pin.types.OUTPUT,unit=1),
            Pin(num='32',name='A4',func=Pin.types.OUTPUT,unit=1),
            Pin(num='33',name='A5',func=Pin.types.OUTPUT,unit=1),
            Pin(num='34',name='A6',func=Pin.types.OUTPUT,unit=1),
            Pin(num='35',name='A7',func=Pin.types.OUTPUT,unit=1),
            Pin(num='36',name='A8',func=Pin.types.OUTPUT,unit=1),
            Pin(num='37',name='A9',func=Pin.types.OUTPUT,unit=1),
            Pin(num='38',name='A10',func=Pin.types.OUTPUT,unit=1),
            Pin(num='39',name='A11',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='D1',func=Pin.types.BIDIR,unit=1),
            Pin(num='40',name='A12',func=Pin.types.OUTPUT,unit=1),
            Pin(num='41',name='A13',func=Pin.types.OUTPUT,unit=1),
            Pin(num='42',name='A14',func=Pin.types.OUTPUT,unit=1),
            Pin(num='43',name='A15',func=Pin.types.OUTPUT,unit=1),
            Pin(num='44',name='A16',func=Pin.types.OUTPUT,unit=1),
            Pin(num='45',name='A17',func=Pin.types.OUTPUT,unit=1),
            Pin(num='46',name='A18',func=Pin.types.OUTPUT,unit=1),
            Pin(num='47',name='A19',func=Pin.types.OUTPUT,unit=1),
            Pin(num='48',name='A20',func=Pin.types.OUTPUT,unit=1),
            Pin(num='49',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='D0',func=Pin.types.BIDIR,unit=1),
            Pin(num='50',name='A21',func=Pin.types.OUTPUT,unit=1),
            Pin(num='51',name='A22',func=Pin.types.OUTPUT,unit=1),
            Pin(num='52',name='A23',func=Pin.types.OUTPUT,unit=1),
            Pin(num='53',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='54',name='D15',func=Pin.types.BIDIR,unit=1),
            Pin(num='55',name='D14',func=Pin.types.BIDIR,unit=1),
            Pin(num='56',name='D13',func=Pin.types.BIDIR,unit=1),
            Pin(num='57',name='D12',func=Pin.types.BIDIR,unit=1),
            Pin(num='58',name='D11',func=Pin.types.BIDIR,unit=1),
            Pin(num='59',name='D10',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='AS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='60',name='D9',func=Pin.types.BIDIR,unit=1),
            Pin(num='61',name='D8',func=Pin.types.BIDIR,unit=1),
            Pin(num='62',name='D7',func=Pin.types.BIDIR,unit=1),
            Pin(num='63',name='D6',func=Pin.types.BIDIR,unit=1),
            Pin(num='64',name='D5',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='UDS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='LDS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='9',name='R/W',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'68008D', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'68008D'}), 'ref_prefix':'U', 'fplist':[''], 'footprint':'', 'keywords':'68000 Microprocessor CPU', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/reference-manual/MC68000UM.pdf', 'pins':[
            Pin(num='1',name='A3',func=Pin.types.TRISTATE,unit=1),
            Pin(num='10',name='A12',func=Pin.types.TRISTATE,unit=1),
            Pin(num='11',name='A13',func=Pin.types.TRISTATE,unit=1),
            Pin(num='12',name='A14',func=Pin.types.TRISTATE,unit=1),
            Pin(num='13',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='14',name='A15',func=Pin.types.TRISTATE,unit=1),
            Pin(num='15',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='16',name='A16',func=Pin.types.TRISTATE,unit=1),
            Pin(num='17',name='A17',func=Pin.types.TRISTATE,unit=1),
            Pin(num='18',name='A18',func=Pin.types.TRISTATE,unit=1),
            Pin(num='19',name='A19',func=Pin.types.TRISTATE,unit=1),
            Pin(num='2',name='A4',func=Pin.types.TRISTATE,unit=1),
            Pin(num='20',name='D7',func=Pin.types.TRISTATE,unit=1),
            Pin(num='21',name='D6',func=Pin.types.TRISTATE,unit=1),
            Pin(num='22',name='D5',func=Pin.types.TRISTATE,unit=1),
            Pin(num='23',name='D4',func=Pin.types.TRISTATE,unit=1),
            Pin(num='24',name='D3',func=Pin.types.TRISTATE,unit=1),
            Pin(num='25',name='D2',func=Pin.types.TRISTATE,unit=1),
            Pin(num='26',name='D1',func=Pin.types.TRISTATE,unit=1),
            Pin(num='27',name='D0',func=Pin.types.TRISTATE,unit=1),
            Pin(num='28',name='AS',func=Pin.types.TRISTATE,unit=1),
            Pin(num='29',name='DS',func=Pin.types.TRISTATE,unit=1),
            Pin(num='3',name='A5',func=Pin.types.TRISTATE,unit=1),
            Pin(num='30',name='R/W',func=Pin.types.TRISTATE,unit=1),
            Pin(num='31',name='DTACK',func=Pin.types.INPUT,unit=1),
            Pin(num='32',name='BG',func=Pin.types.OUTPUT,unit=1),
            Pin(num='33',name='BR',func=Pin.types.INPUT,unit=1),
            Pin(num='34',name='CLK',func=Pin.types.INPUT,unit=1),
            Pin(num='35',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='36',name='HALT',func=Pin.types.BIDIR,unit=1),
            Pin(num='37',name='RESET',func=Pin.types.BIDIR,unit=1),
            Pin(num='38',name='E',func=Pin.types.OUTPUT,unit=1),
            Pin(num='39',name='VPA',func=Pin.types.INPUT,unit=1),
            Pin(num='4',name='A6',func=Pin.types.TRISTATE,unit=1),
            Pin(num='40',name='BERR',func=Pin.types.INPUT,unit=1),
            Pin(num='41',name='IPL1',func=Pin.types.INPUT,unit=1),
            Pin(num='42',name='IPL0/2',func=Pin.types.INPUT,unit=1),
            Pin(num='43',name='FC2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='44',name='FC1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='45',name='FC0',func=Pin.types.OUTPUT,unit=1),
            Pin(num='46',name='A0',func=Pin.types.TRISTATE,unit=1),
            Pin(num='47',name='A1',func=Pin.types.TRISTATE,unit=1),
            Pin(num='48',name='A2',func=Pin.types.TRISTATE,unit=1),
            Pin(num='5',name='A7',func=Pin.types.TRISTATE,unit=1),
            Pin(num='6',name='A8',func=Pin.types.TRISTATE,unit=1),
            Pin(num='7',name='A9',func=Pin.types.TRISTATE,unit=1),
            Pin(num='8',name='A10',func=Pin.types.TRISTATE,unit=1),
            Pin(num='9',name='A11',func=Pin.types.TRISTATE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MC68000FN', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC68000FN'}), 'ref_prefix':'U', 'fplist':['Package_LCC:PLCC-68'], 'footprint':'Package_LCC:PLCC-68', 'keywords':'MPRO', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/reference-manual/MC68000UM.pdf', 'pins':[
            Pin(num='1',name='D4',func=Pin.types.BIDIR,unit=1),
            Pin(num='10',name='DTACK',func=Pin.types.INPUT,unit=1),
            Pin(num='11',name='BG',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='BGACK',func=Pin.types.INPUT,unit=1),
            Pin(num='13',name='BR',func=Pin.types.INPUT,unit=1),
            Pin(num='14',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='15',name='CLK',func=Pin.types.INPUT,unit=1),
            Pin(num='16',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='17',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='18',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='19',name='HALT',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='D3',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='RESET',func=Pin.types.INPUT,unit=1),
            Pin(num='21',name='VMA',func=Pin.types.OUTPUT,unit=1),
            Pin(num='22',name='E',func=Pin.types.OUTPUT,unit=1),
            Pin(num='23',name='VPA',func=Pin.types.INPUT,unit=1),
            Pin(num='24',name='BERR',func=Pin.types.INPUT,unit=1),
            Pin(num='25',name='IPL2',func=Pin.types.INPUT,unit=1),
            Pin(num='26',name='IPL1',func=Pin.types.INPUT,unit=1),
            Pin(num='27',name='IPL0',func=Pin.types.INPUT,unit=1),
            Pin(num='28',name='FC2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='29',name='FC1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='3',name='D2',func=Pin.types.BIDIR,unit=1),
            Pin(num='30',name='FC0',func=Pin.types.OUTPUT,unit=1),
            Pin(num='31',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='32',name='A1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='33',name='A2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='34',name='A3',func=Pin.types.OUTPUT,unit=1),
            Pin(num='35',name='A4',func=Pin.types.OUTPUT,unit=1),
            Pin(num='36',name='A5',func=Pin.types.OUTPUT,unit=1),
            Pin(num='37',name='A6',func=Pin.types.OUTPUT,unit=1),
            Pin(num='38',name='A7',func=Pin.types.OUTPUT,unit=1),
            Pin(num='39',name='A8',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='D1',func=Pin.types.BIDIR,unit=1),
            Pin(num='40',name='A9',func=Pin.types.OUTPUT,unit=1),
            Pin(num='41',name='A10',func=Pin.types.OUTPUT,unit=1),
            Pin(num='42',name='A11',func=Pin.types.OUTPUT,unit=1),
            Pin(num='43',name='A12',func=Pin.types.OUTPUT,unit=1),
            Pin(num='44',name='A13',func=Pin.types.OUTPUT,unit=1),
            Pin(num='45',name='A14',func=Pin.types.OUTPUT,unit=1),
            Pin(num='46',name='A15',func=Pin.types.OUTPUT,unit=1),
            Pin(num='47',name='A16',func=Pin.types.OUTPUT,unit=1),
            Pin(num='48',name='A17',func=Pin.types.OUTPUT,unit=1),
            Pin(num='49',name='A18',func=Pin.types.OUTPUT,unit=1),
            Pin(num='5',name='D0',func=Pin.types.BIDIR,unit=1),
            Pin(num='50',name='A19',func=Pin.types.OUTPUT,unit=1),
            Pin(num='51',name='A20',func=Pin.types.OUTPUT,unit=1),
            Pin(num='52',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='53',name='A21',func=Pin.types.OUTPUT,unit=1),
            Pin(num='54',name='A22',func=Pin.types.OUTPUT,unit=1),
            Pin(num='55',name='A23',func=Pin.types.OUTPUT,unit=1),
            Pin(num='56',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='57',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='58',name='D15',func=Pin.types.BIDIR,unit=1),
            Pin(num='59',name='D14',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='AS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='60',name='D13',func=Pin.types.BIDIR,unit=1),
            Pin(num='61',name='D12',func=Pin.types.BIDIR,unit=1),
            Pin(num='62',name='D11',func=Pin.types.BIDIR,unit=1),
            Pin(num='63',name='D10',func=Pin.types.BIDIR,unit=1),
            Pin(num='64',name='D9',func=Pin.types.BIDIR,unit=1),
            Pin(num='65',name='D8',func=Pin.types.BIDIR,unit=1),
            Pin(num='66',name='D7',func=Pin.types.BIDIR,unit=1),
            Pin(num='67',name='D6',func=Pin.types.BIDIR,unit=1),
            Pin(num='68',name='D5',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='UDS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='LDS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='9',name='R/W',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'MC68332', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'MC68332'}), 'ref_prefix':'U', 'fplist':['Package_QFP:PQFP-132_24x24mm_P0.635mm'], 'footprint':'Package_QFP:PQFP-132_24x24mm_P0.635mm', 'keywords':'MCU 32 bit', 'description':'', 'datasheet':'http://pdf.datasheetcatalog.com/datasheet/motorola/SPAKMC332AVFC20.pdf', 'pins':[
            Pin(num='2',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='TP6',func=Pin.types.INPUT,unit=1),
            Pin(num='100',name='D8',func=Pin.types.INPUT,unit=1),
            Pin(num='101',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='102',name='D7',func=Pin.types.INPUT,unit=1),
            Pin(num='103',name='D6',func=Pin.types.INPUT,unit=1),
            Pin(num='104',name='D5',func=Pin.types.INPUT,unit=1),
            Pin(num='105',name='D4',func=Pin.types.INPUT,unit=1),
            Pin(num='106',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='107',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='108',name='D3',func=Pin.types.INPUT,unit=1),
            Pin(num='109',name='D2',func=Pin.types.INPUT,unit=1),
            Pin(num='11',name='TP5',func=Pin.types.INPUT,unit=1),
            Pin(num='110',name='D1',func=Pin.types.INPUT,unit=1),
            Pin(num='111',name='D0',func=Pin.types.INPUT,unit=1),
            Pin(num='112',name='CSBOOT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='113',name='BR/CS0',func=Pin.types.INPUT,unit=1),
            Pin(num='114',name='BG/CS1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='115',name='BGACK/CS2',func=Pin.types.INPUT,unit=1),
            Pin(num='116',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='117',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='118',name='FC0/CS3',func=Pin.types.OUTPUT,unit=1),
            Pin(num='119',name='FC1/CS4',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='TP4',func=Pin.types.INPUT,unit=1),
            Pin(num='120',name='FC2/CS5',func=Pin.types.OUTPUT,unit=1),
            Pin(num='121',name='A19/CS6',func=Pin.types.OUTPUT,unit=1),
            Pin(num='122',name='A20/CS7',func=Pin.types.OUTPUT,unit=1),
            Pin(num='123',name='A21/CS8',func=Pin.types.OUTPUT,unit=1),
            Pin(num='124',name='A22/CS9',func=Pin.types.OUTPUT,unit=1),
            Pin(num='125',name='A23/CS10',func=Pin.types.OUTPUT,unit=1),
            Pin(num='126',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='127',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='128',name='T2CLK',func=Pin.types.INPUT,unit=1),
            Pin(num='129',name='TP15',func=Pin.types.INPUT,unit=1),
            Pin(num='13',name='TP3',func=Pin.types.INPUT,unit=1),
            Pin(num='130',name='TP14',func=Pin.types.INPUT,unit=1),
            Pin(num='131',name='TP13',func=Pin.types.INPUT,unit=1),
            Pin(num='132',name='TP12',func=Pin.types.INPUT,unit=1),
            Pin(num='14',name='TP2',func=Pin.types.INPUT,unit=1),
            Pin(num='15',name='TP1',func=Pin.types.INPUT,unit=1),
            Pin(num='16',name='TP0',func=Pin.types.INPUT,unit=1),
            Pin(num='17',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='18',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='19',name='VSTBY',func=Pin.types.INPUT,unit=1),
            Pin(num='20',name='A1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='21',name='A2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='22',name='A3',func=Pin.types.OUTPUT,unit=1),
            Pin(num='23',name='A4',func=Pin.types.OUTPUT,unit=1),
            Pin(num='24',name='A5',func=Pin.types.OUTPUT,unit=1),
            Pin(num='25',name='A6',func=Pin.types.OUTPUT,unit=1),
            Pin(num='26',name='A7',func=Pin.types.OUTPUT,unit=1),
            Pin(num='27',name='A8',func=Pin.types.OUTPUT,unit=1),
            Pin(num='28',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='29',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='TP11',func=Pin.types.INPUT,unit=1),
            Pin(num='30',name='A9',func=Pin.types.OUTPUT,unit=1),
            Pin(num='31',name='A10',func=Pin.types.OUTPUT,unit=1),
            Pin(num='32',name='A11',func=Pin.types.OUTPUT,unit=1),
            Pin(num='33',name='A12',func=Pin.types.OUTPUT,unit=1),
            Pin(num='34',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='35',name='A13',func=Pin.types.OUTPUT,unit=1),
            Pin(num='36',name='A14',func=Pin.types.OUTPUT,unit=1),
            Pin(num='37',name='A15',func=Pin.types.OUTPUT,unit=1),
            Pin(num='38',name='A16',func=Pin.types.OUTPUT,unit=1),
            Pin(num='39',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='TP10',func=Pin.types.INPUT,unit=1),
            Pin(num='40',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='41',name='A17',func=Pin.types.OUTPUT,unit=1),
            Pin(num='42',name='A18',func=Pin.types.OUTPUT,unit=1),
            Pin(num='43',name='MISO',func=Pin.types.INPUT,unit=1),
            Pin(num='44',name='MOSI',func=Pin.types.INPUT,unit=1),
            Pin(num='45',name='SCK',func=Pin.types.INPUT,unit=1),
            Pin(num='46',name='PSCO/SS',func=Pin.types.INPUT,unit=1),
            Pin(num='47',name='PCS1',func=Pin.types.INPUT,unit=1),
            Pin(num='48',name='PCS2',func=Pin.types.INPUT,unit=1),
            Pin(num='49',name='PCS3',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='TP9',func=Pin.types.INPUT,unit=1),
            Pin(num='50',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='51',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='52',name='TXD',func=Pin.types.INPUT,unit=1),
            Pin(num='53',name='RXD',func=Pin.types.INPUT,unit=1),
            Pin(num='54',name='IPIPE/DSO',func=Pin.types.OUTPUT,unit=1),
            Pin(num='55',name='IFETCH/DSI',func=Pin.types.INPUT,unit=1),
            Pin(num='56',name='BKPT/DSCLK',func=Pin.types.INPUT,unit=1),
            Pin(num='57',name='TSTME/TSC',func=Pin.types.INPUT,unit=1),
            Pin(num='58',name='FREEZE/QUOT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='59',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='TP8',func=Pin.types.INPUT,unit=1),
            Pin(num='60',name='XTAL',func=Pin.types.OUTPUT,unit=1),
            Pin(num='61',name='VDDSYN',func=Pin.types.INPUT,unit=1),
            Pin(num='62',name='EXTAL',func=Pin.types.INPUT,unit=1),
            Pin(num='63',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='64',name='XFC',func=Pin.types.INPUT,unit=1),
            Pin(num='65',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='66',name='CLKOUT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='67',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='68',name='RESET',func=Pin.types.INPUT,unit=1),
            Pin(num='69',name='HALT',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='70',name='BERR',func=Pin.types.INPUT,unit=1),
            Pin(num='71',name='IRQ7',func=Pin.types.INPUT,unit=1),
            Pin(num='72',name='IRQ6',func=Pin.types.INPUT,unit=1),
            Pin(num='73',name='IRQ5',func=Pin.types.INPUT,unit=1),
            Pin(num='74',name='IRQ4',func=Pin.types.INPUT,unit=1),
            Pin(num='75',name='IRQ3',func=Pin.types.INPUT,unit=1),
            Pin(num='76',name='IRQ2',func=Pin.types.INPUT,unit=1),
            Pin(num='77',name='IRQ1',func=Pin.types.INPUT,unit=1),
            Pin(num='78',name='MODCK',func=Pin.types.INPUT,unit=1),
            Pin(num='79',name='R/W',func=Pin.types.INPUT,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='80',name='SIZ1',func=Pin.types.INPUT,unit=1),
            Pin(num='81',name='SIZ0',func=Pin.types.INPUT,unit=1),
            Pin(num='82',name='AS',func=Pin.types.INPUT,unit=1),
            Pin(num='83',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='84',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='85',name='DS',func=Pin.types.INPUT,unit=1),
            Pin(num='86',name='RMC',func=Pin.types.INPUT,unit=1),
            Pin(num='87',name='AVEC',func=Pin.types.INPUT,unit=1),
            Pin(num='88',name='DSACK1',func=Pin.types.INPUT,unit=1),
            Pin(num='89',name='DSACK0',func=Pin.types.INPUT,unit=1),
            Pin(num='9',name='TP7',func=Pin.types.INPUT,unit=1),
            Pin(num='90',name='A0',func=Pin.types.OUTPUT,unit=1),
            Pin(num='91',name='D15',func=Pin.types.INPUT,unit=1),
            Pin(num='92',name='D14',func=Pin.types.INPUT,unit=1),
            Pin(num='93',name='D13',func=Pin.types.INPUT,unit=1),
            Pin(num='94',name='D12',func=Pin.types.INPUT,unit=1),
            Pin(num='95',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='96',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='97',name='D11',func=Pin.types.INPUT,unit=1),
            Pin(num='98',name='D10',func=Pin.types.INPUT,unit=1),
            Pin(num='99',name='D9',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'68010D', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'68010D'}), 'ref_prefix':'U', 'fplist':['', ''], 'footprint':'', 'keywords':'68000 Microprocessor CPU', 'description':'', 'datasheet':'https://www.nxp.com/docs/en/reference-manual/MC68000UM.pdf', 'pins':[
            Pin(num='1',name='D4',func=Pin.types.BIDIR,unit=1),
            Pin(num='10',name='DTACK',func=Pin.types.INPUT,unit=1),
            Pin(num='11',name='BG',func=Pin.types.OUTPUT,unit=1),
            Pin(num='12',name='BGACK',func=Pin.types.INPUT,unit=1),
            Pin(num='13',name='BR',func=Pin.types.INPUT,unit=1),
            Pin(num='14',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='15',name='CLK',func=Pin.types.INPUT,unit=1),
            Pin(num='16',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='17',name='HALT',func=Pin.types.BIDIR,unit=1),
            Pin(num='18',name='RESET',func=Pin.types.BIDIR,unit=1),
            Pin(num='19',name='VMA',func=Pin.types.OUTPUT,unit=1),
            Pin(num='2',name='D3',func=Pin.types.BIDIR,unit=1),
            Pin(num='20',name='E',func=Pin.types.OUTPUT,unit=1),
            Pin(num='21',name='VPA',func=Pin.types.INPUT,unit=1),
            Pin(num='22',name='BERR',func=Pin.types.INPUT,unit=1),
            Pin(num='23',name='IPL2',func=Pin.types.INPUT,unit=1),
            Pin(num='24',name='IPL1',func=Pin.types.INPUT,unit=1),
            Pin(num='25',name='IPL0',func=Pin.types.INPUT,unit=1),
            Pin(num='26',name='FC2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='27',name='FC1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='28',name='FC0',func=Pin.types.OUTPUT,unit=1),
            Pin(num='29',name='A1',func=Pin.types.OUTPUT,unit=1),
            Pin(num='3',name='D2',func=Pin.types.BIDIR,unit=1),
            Pin(num='30',name='A2',func=Pin.types.OUTPUT,unit=1),
            Pin(num='31',name='A3',func=Pin.types.OUTPUT,unit=1),
            Pin(num='32',name='A4',func=Pin.types.OUTPUT,unit=1),
            Pin(num='33',name='A5',func=Pin.types.OUTPUT,unit=1),
            Pin(num='34',name='A6',func=Pin.types.OUTPUT,unit=1),
            Pin(num='35',name='A7',func=Pin.types.OUTPUT,unit=1),
            Pin(num='36',name='A8',func=Pin.types.OUTPUT,unit=1),
            Pin(num='37',name='A9',func=Pin.types.OUTPUT,unit=1),
            Pin(num='38',name='A10',func=Pin.types.OUTPUT,unit=1),
            Pin(num='39',name='A11',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='D1',func=Pin.types.BIDIR,unit=1),
            Pin(num='40',name='A12',func=Pin.types.OUTPUT,unit=1),
            Pin(num='41',name='A13',func=Pin.types.OUTPUT,unit=1),
            Pin(num='42',name='A14',func=Pin.types.OUTPUT,unit=1),
            Pin(num='43',name='A15',func=Pin.types.OUTPUT,unit=1),
            Pin(num='44',name='A16',func=Pin.types.OUTPUT,unit=1),
            Pin(num='45',name='A17',func=Pin.types.OUTPUT,unit=1),
            Pin(num='46',name='A18',func=Pin.types.OUTPUT,unit=1),
            Pin(num='47',name='A19',func=Pin.types.OUTPUT,unit=1),
            Pin(num='48',name='A20',func=Pin.types.OUTPUT,unit=1),
            Pin(num='49',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='D0',func=Pin.types.BIDIR,unit=1),
            Pin(num='50',name='A21',func=Pin.types.OUTPUT,unit=1),
            Pin(num='51',name='A22',func=Pin.types.OUTPUT,unit=1),
            Pin(num='52',name='A23',func=Pin.types.OUTPUT,unit=1),
            Pin(num='53',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='54',name='D15',func=Pin.types.BIDIR,unit=1),
            Pin(num='55',name='D14',func=Pin.types.BIDIR,unit=1),
            Pin(num='56',name='D13',func=Pin.types.BIDIR,unit=1),
            Pin(num='57',name='D12',func=Pin.types.BIDIR,unit=1),
            Pin(num='58',name='D11',func=Pin.types.BIDIR,unit=1),
            Pin(num='59',name='D10',func=Pin.types.BIDIR,unit=1),
            Pin(num='6',name='AS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='60',name='D9',func=Pin.types.BIDIR,unit=1),
            Pin(num='61',name='D8',func=Pin.types.BIDIR,unit=1),
            Pin(num='62',name='D7',func=Pin.types.BIDIR,unit=1),
            Pin(num='63',name='D6',func=Pin.types.BIDIR,unit=1),
            Pin(num='64',name='D5',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='UDS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='8',name='LDS',func=Pin.types.OUTPUT,unit=1),
            Pin(num='9',name='R/W',func=Pin.types.OUTPUT,unit=1)], 'unit_defs':[] })])