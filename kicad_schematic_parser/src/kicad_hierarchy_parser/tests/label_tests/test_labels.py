import pytest
from kiutils.schematic import Schematic, HierarchicalSheet, HierarchicalPin, Position, Property, Effects
from skidl_kicad_parser.labels.label_parser import parse_labels

def test_sheet_pin_parsing():
    """Test parsing of sheet pins into hierarchical labels"""
    # Create a test schematic with a sheet containing pins
    schematic = Schematic()
    
    # Create a sheet with test pins
    sheet = HierarchicalSheet()
    # Add sheet name property
    sheet.sheetName = Property(key='Sheetname', value='TestSheet')
    sheet.pins = [
        HierarchicalPin(
            name='test_pin1',
            connectionType='input',
            position=Position(X=100.0, Y=50.0, angle=0),
            uuid='test-uuid-1'
        ),
        HierarchicalPin(
            name='test_pin2',
            connectionType='output',
            position=Position(X=150.0, Y=75.0, angle=180),
            uuid='test-uuid-2'
        )
    ]
    schematic.sheets = [sheet]
    
    # Parse labels
    labels = parse_labels(schematic)
    
    # Verify hierarchical labels (sheet pins)
    assert len(labels['hierarchical']) == 2
    
    # Check first pin
    pin1 = next(l for l in labels['hierarchical'] if l['text'] == 'test_pin1')
    assert pin1['shape'] == 'input'
    assert pin1['position'] == (100.0, 50.0)
    assert pin1['angle'] == 0
    assert pin1['uuid'] == 'test-uuid-1'
    assert pin1['sheet_name'] == 'TestSheet'
    
    # Check second pin
    pin2 = next(l for l in labels['hierarchical'] if l['text'] == 'test_pin2')
    assert pin2['shape'] == 'output'
    assert pin2['position'] == (150.0, 75.0)
    assert pin2['angle'] == 180
    assert pin2['uuid'] == 'test-uuid-2'
    assert pin2['sheet_name'] == 'TestSheet'
    
    # Verify other label types are empty (no regular labels in test)
    assert len(labels['local']) == 0
    assert len(labels['power']) == 0

def test_mixed_label_parsing():
    """Test parsing of both regular hierarchical labels and sheet pins"""
    # Create a test schematic with both types of labels
    schematic = Schematic()
    
    # Add a sheet with a pin
    sheet = HierarchicalSheet()
    sheet.sheetName = Property(key='Sheetname', value='TestSheet')
    sheet.pins = [
        HierarchicalPin(
            name='sheet_pin',
            connectionType='input',
            position=Position(X=100.0, Y=50.0, angle=0),
            uuid='test-uuid-1'
        )
    ]
    schematic.sheets = [sheet]
    
    # Add a regular hierarchical label
    class HierarchicalLabel:
        def __init__(self):
            self.text = 'test_label'
            self.shape = 'output'
            self.position = Position(X=200.0, Y=75.0, angle=0)
    
    schematic.hierarchicalLabels = [HierarchicalLabel()]
    
    # Parse labels
    labels = parse_labels(schematic)
    
    # Verify both types are present
    assert len(labels['hierarchical']) == 2
    
    # Check sheet pin
    sheet_pin = next(l for l in labels['hierarchical'] if l['text'] == 'sheet_pin')
    assert sheet_pin['shape'] == 'input'
    assert sheet_pin['position'] == (100.0, 50.0)
    assert sheet_pin['uuid'] == 'test-uuid-1'
    assert sheet_pin['sheet_name'] == 'TestSheet'
    
    # Check hierarchical label
    hier = next(l for l in labels['hierarchical'] if l['text'] == 'test_label')
    assert hier['shape'] == 'output'
    assert hier['position'] == (200.0, 75.0)
    assert 'uuid' not in hier  # Regular hierarchical labels don't have UUIDs
    assert 'sheet_name' not in hier  # Regular hierarchical labels don't have sheet names
