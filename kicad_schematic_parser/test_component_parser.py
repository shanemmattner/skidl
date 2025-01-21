import pytest
from component_parser import parse_component_name, parse_component_properties, Component

def test_valid_component():
    """Test parsing a valid component line"""
    result = parse_component_name("Component: Device/R")
    assert result.success
    assert result.data == ("Device", "R")
    assert not result.errors

def test_complex_component():
    """Test parsing a component with more complex names"""
    result = parse_component_name("Component: RF_Module/ESP32-S3-MINI-1")
    assert result.success
    assert result.data == ("RF_Module", "ESP32-S3-MINI-1")
    assert not result.errors

def test_missing_component_prefix():
    """Test line without 'Component:' prefix"""
    result = parse_component_name("Device/R")
    assert not result.success
    assert len(result.errors) == 1
    assert "must start with 'Component:'" in result.errors[0].message

def test_missing_slash():
    """Test component without library/component separator"""
    result = parse_component_name("Component: DeviceR")
    assert not result.success
    assert len(result.errors) == 1
    assert "must be in format" in result.errors[0].message

def test_empty_library():
    """Test component with empty library name"""
    result = parse_component_name("Component: /R")
    assert not result.success
    assert len(result.errors) == 1
    assert "must not be empty" in result.errors[0].message

def test_empty_component():
    """Test component with empty component name"""
    result = parse_component_name("Component: Device/")
    assert not result.success
    assert len(result.errors) == 1
    assert "must not be empty" in result.errors[0].message

def test_malformed_line():
    """Test completely malformed line"""
    result = parse_component_name("Component:")
    assert not result.success
    assert len(result.errors) == 1

def test_basic_properties():
    """Test parsing basic component properties"""
    lines = [
        "Properties:",
        "    Reference: R1",
        "    Value: 10K",
        "    Footprint: Resistor_SMD:R_0603_1608Metric"
    ]
    result = parse_component_properties(lines)
    assert result.success
    assert result.data.reference == "R1"
    assert result.data.value == "10K"
    assert result.data.footprint == "Resistor_SMD:R_0603_1608Metric"

def test_full_properties():
    """Test parsing full component properties including description"""
    lines = [
        "Properties:",
        "    Reference: U1",
        "    Value: ESP32-S3-MINI-1",
        "    Footprint: RF_Module:ESP32-S2-MINI-1",
        "    Datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-s3-mini-1_mini-1u_datasheet_en.pdf",
        "    Description: RF Module, ESP32-S3 SoC, Wi-Fi 802.11b/g/n, BLE"
    ]
    result = parse_component_properties(lines)
    assert result.success
    assert result.data.reference == "U1"
    assert result.data.value == "ESP32-S3-MINI-1"
    assert result.data.footprint == "RF_Module:ESP32-S2-MINI-1"
    assert result.data.datasheet.startswith("https://")
    assert result.data.description.startswith("RF Module")

def test_properties_with_uuid():
    """Test parsing properties with UUID"""
    lines = [
        "Properties:",
        "    Reference: U1",
        "    Value: ESP32-S3-MINI-1",
        "    UUID: e6f5f316-cb92-4d26-9a5c-0bb6c841d4b0"
    ]
    result = parse_component_properties(lines)
    assert result.success
    assert result.data.reference == "U1"
    assert result.data.uuid == "e6f5f316-cb92-4d26-9a5c-0bb6c841d4b0"

def test_invalid_properties():
    """Test parsing invalid properties section"""
    lines = [
        "Properties:",
        "Reference: R1",  # Missing indentation
        "    Value"       # Missing value
    ]
    result = parse_component_properties(lines)
    assert not result.success
    assert len(result.errors) == 3
    # Check for indentation error
    assert any("must be indented" in err.message for err in result.errors)
    # Check for missing value error
    assert any("must be in format" in err.message for err in result.errors)
    # Check for missing required fields error
    assert any("must have Reference and Value" in err.message for err in result.errors)