from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

Sensor_Distance = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'TMF8820', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TMF8820'}), 'ref_prefix':'U', 'fplist':['Sensor_Distance:AMS_OLGA12'], 'footprint':'Sensor_Distance:AMS_OLGA12', 'keywords':'TMF882x ToF', 'description':'', 'datasheet':'https://ams.com/documents/20143/6015057/TMF882X_DS000693_8-00.pdf', 'pins':[
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='GPIO1',func=Pin.types.TRISTATE,unit=1),
            Pin(num='11',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='12',name='VDD',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GPIO0',func=Pin.types.TRISTATE,unit=1),
            Pin(num='4',name='INT',func=Pin.types.OPENCOLL,unit=1),
            Pin(num='5',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='VDD',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='9',name='EN',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VL53L1CXV0FY1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VL53L1CXV0FY1'}), 'ref_prefix':'U', 'fplist':['Sensor_Distance:ST_VL53L1x'], 'footprint':'Sensor_Distance:ST_VL53L1x', 'keywords':'VL53L1x ToF', 'description':'', 'datasheet':'https://www.st.com/resource/en/datasheet/vl53l1x.pdf', 'pins':[
            Pin(num='1',name='AVDDVCSEL',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='11',name='AVDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='12',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='AVSSVCSEL',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='XSHUT',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='7',name='GPIO1',func=Pin.types.OPENCOLL,unit=1),
            Pin(num='8',name='DNC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='9',name='SDA',func=Pin.types.BIDIR,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TMF8821', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TMF8821'}), 'ref_prefix':'U', 'fplist':['Sensor_Distance:AMS_OLGA12', 'Sensor_Distance:AMS_OLGA12'], 'footprint':'Sensor_Distance:AMS_OLGA12', 'keywords':'TMF882x ToF', 'description':'', 'datasheet':'https://ams.com/documents/20143/6015057/TMF882X_DS000693_8-00.pdf', 'pins':[
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='GPIO1',func=Pin.types.TRISTATE,unit=1),
            Pin(num='11',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='12',name='VDD',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GPIO0',func=Pin.types.TRISTATE,unit=1),
            Pin(num='4',name='INT',func=Pin.types.OPENCOLL,unit=1),
            Pin(num='5',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='VDD',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='9',name='EN',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'TMF8828', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TMF8828'}), 'ref_prefix':'U', 'fplist':['Sensor_Distance:AMS_OLGA12', 'Sensor_Distance:AMS_OLGA12', 'Sensor_Distance:AMS_OLGA12'], 'footprint':'Sensor_Distance:AMS_OLGA12', 'keywords':'TMF882x ToF', 'description':'', 'datasheet':'https://ams.com/documents/20143/6015057/TMF882X_DS000693_8-00.pdf', 'pins':[
            Pin(num='1',name='VDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='GPIO1',func=Pin.types.TRISTATE,unit=1),
            Pin(num='11',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='12',name='VDD',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GPIO0',func=Pin.types.TRISTATE,unit=1),
            Pin(num='4',name='INT',func=Pin.types.OPENCOLL,unit=1),
            Pin(num='5',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='SDA',func=Pin.types.BIDIR,unit=1),
            Pin(num='7',name='VDD',func=Pin.types.PASSIVE,unit=1),
            Pin(num='8',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='9',name='EN',func=Pin.types.INPUT,unit=1)], 'unit_defs':[] }),
        Part(**{ 'name':'VL53L0CXV0DH1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'VL53L0CXV0DH1'}), 'ref_prefix':'U', 'fplist':['Sensor_Distance:ST_VL53L1x', 'Sensor_Distance:ST_VL53L1x'], 'footprint':'Sensor_Distance:ST_VL53L1x', 'keywords':'VL53L0x ToF', 'description':'', 'datasheet':'https://www.st.com/resource/en/datasheet/vl53l0x.pdf', 'pins':[
            Pin(num='1',name='AVDDVCSEL',func=Pin.types.PWRIN,unit=1),
            Pin(num='10',name='SCL',func=Pin.types.INPUT,unit=1),
            Pin(num='11',name='AVDD',func=Pin.types.PWRIN,unit=1),
            Pin(num='12',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='2',name='AVSSVCSEL',func=Pin.types.PWRIN,unit=1),
            Pin(num='3',name='GND',func=Pin.types.PWRIN,unit=1),
            Pin(num='4',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='5',name='XSHUT',func=Pin.types.INPUT,unit=1),
            Pin(num='6',name='GND',func=Pin.types.PASSIVE,unit=1),
            Pin(num='7',name='GPIO1',func=Pin.types.OPENCOLL,unit=1),
            Pin(num='8',name='DNC',func=Pin.types.NOCONNECT,unit=1),
            Pin(num='9',name='SDA',func=Pin.types.BIDIR,unit=1)], 'unit_defs':[] })])