from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Sensor_Humidity = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'ENS210', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'ENS210'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:AMS_QFN-4-1EP_2x2mm_P0.95mm_EP0.7x1.6mm'], 'footprint':'Package_DFN_QFN:AMS_QFN-4-1EP_2x2mm_P0.95mm_EP0.7x1.6mm', 'keywords':'relative humidity temperature i2c pre-calibrated', 'description':'', 'datasheet':'http://ams.com/eng/Products/Environmental-Sensors/Relative-Humidity-and-Temperature-Sensors/ENS210', 'pins':[
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='GND',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'HDC1080', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HDC1080'}), 'ref_prefix':'U', 'fplist':['Package_SON:Texas_PWSON-N6'], 'footprint':'Package_SON:Texas_PWSON-N6', 'keywords':'Temperature Humidity Sensor', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/hdc1080.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='5',name='VCC',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='DAP',func=Pin.types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'HDC2080', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'HDC2080'}), 'ref_prefix':'U', 'fplist':['Package_SON:Texas_PWSON-N6'], 'footprint':'Package_SON:Texas_PWSON-N6', 'keywords':'Temperature Humidity Sensor', 'description':'', 'datasheet':'http://www.ti.com/lit/ds/symlink/hdc2080.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='4',name='DRDY',func=Pin.types.OUTPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='EP',func=Pin.types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT31-DIS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT31-DIS'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'keywords':'digital temperature humidity i2c', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='ALERT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='~{RESET}',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='R',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='VSS',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT4x', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT4x'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad'], 'footprint':'Sensor_Humidity:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad', 'keywords':'Sensirion environment environmental measurement digital SHT40 SHT41 SHT45', 'description':'', 'datasheet':'https://sensirion.com/media/documents/33FD6951/624C4357/Datasheet_SHT4x.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='VSS',func=Pin.types.PWRIN,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHTC1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHTC1'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-4-1EP_2x2mm_P1mm_EP0.7x1.6mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-4-1EP_2x2mm_P1mm_EP0.7x1.6mm', 'keywords':'Sensirion environment environmental measurement digital', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Humidity/Sensirion_Humidity_Sensors_SHTC1_Datasheet.pdf', 'pins':[
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Si7020-A20', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Si7020-A20'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-6-1EP_3x3mm_P1mm_EP1.5x2.4mm'], 'footprint':'Package_DFN_QFN:DFN-6-1EP_3x3mm_P1mm_EP1.5x2.4mm', 'keywords':'I2C Humidity Temperature Sensor', 'description':'', 'datasheet':'https://www.silabs.com/documents/public/data-sheets/Si7020-A20.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='PAD',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT30-DIS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT30-DIS'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'keywords':'digital temperature humidity i2c', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='ALERT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='~{RESET}',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='R',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='VSS',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT30A-DIS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT30A-DIS'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'keywords':'digital temperature humidity automotive i2c', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3xA_Datasheet.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='ALERT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='~{RESET}',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='R',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='VSS',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT31A-DIS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT31A-DIS'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'keywords':'digital temperature humidity automotive i2c', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3xA_Datasheet.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='ALERT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='~{RESET}',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='R',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='VSS',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT35-DIS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT35-DIS'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'keywords':'digital temperature humidity i2c', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='ALERT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='~{RESET}',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='R',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='VSS',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHT35A-DIS', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHT35A-DIS'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-8-1EP_2.5x2.5mm_P0.5mm_EP1.1x1.7mm', 'keywords':'digital temperature humidity automotive i2c', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/2_Humidity_Sensors/Datasheets/Sensirion_Humidity_Sensors_SHT3xA_Datasheet.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='ADDR',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='ALERT',func=Pin.types.OUTPUT,unit=1),
            Pin(num='4',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='~{RESET}',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='R',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='9',name='VSS',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'SHTC3', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SHTC3'}), 'ref_prefix':'U', 'fplist':['Sensor_Humidity:Sensirion_DFN-4-1EP_2x2mm_P1mm_EP0.7x1.6mm', 'Sensor_Humidity:Sensirion_DFN-4-1EP_2x2mm_P1mm_EP0.7x1.6mm'], 'footprint':'Sensor_Humidity:Sensirion_DFN-4-1EP_2x2mm_P1mm_EP0.7x1.6mm', 'keywords':'Sensirion environment environmental measurement digital', 'description':'', 'datasheet':'https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Humidity/Sensirion_Humidity_Sensors_SHTC3_Datasheet.pdf', 'pins':[
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='2',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='3',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='4',name='VSS',func=Pin.types.PWRIN,unit=1),
            Pin(num='5',name='NC',func=Pin.types.NOCONNECT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'Si7021-A20', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Si7021-A20'}), 'ref_prefix':'U', 'fplist':['Package_DFN_QFN:DFN-6-1EP_3x3mm_P1mm_EP1.5x2.4mm', 'Package_DFN_QFN:DFN-6-1EP_3x3mm_P1mm_EP1.5x2.4mm'], 'footprint':'Package_DFN_QFN:DFN-6-1EP_3x3mm_P1mm_EP1.5x2.4mm', 'keywords':'I2C Humidity Temperature Sensor', 'description':'', 'datasheet':'https://www.silabs.com/documents/public/data-sheets/Si7021-A20.pdf', 'pins':[
            Pin(num='1',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='4',name='NC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='5',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='6',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='7',name='PAD',func=Pin.types.PASSIVE,unit=1)], 'unit_defs':[] })])