# Unit Testing Best Practices Guide

## Core Principles

### 1. Test Independence
- Each test should be completely independent and self-contained
- Tests should not rely on the state from other tests
- Use fixtures for setup and teardown
- Avoid global state modifications

### 2. Single Responsibility
- Each test should verify one specific behavior
- Test names should clearly indicate what is being tested
- Follow the Arrange-Act-Assert pattern
- Avoid testing multiple behaviors in one test

### 3. Deterministic Results
- Tests should produce the same result every time they run
- Avoid dependencies on external systems when possible
- Mock external dependencies consistently
- Control random number generators and timestamps

## Practical Implementation

### Test Structure

#### Good Example:
```python
def test_resistor_properties():
    """Test that a resistor's properties are correctly set"""
    # Arrange
    expected_value = "10k"
    expected_footprint = "R_0603_1608Metric"
    
    # Act
    resistor = Part("Device", "R", value=expected_value, footprint=expected_footprint)
    
    # Assert
    assert resistor.value == expected_value
    assert resistor.footprint == expected_footprint
```

#### Bad Example:
```python
def test_resistor():
    """Don't do this - testing too many things"""
    r = Part("Device", "R")
    r.value = "10k"
    assert r.value == "10k"
    assert r.pins  # Unrelated assertion
    r.connect()    # Testing connection in same test
```

### Naming Conventions

- Use descriptive, action-based names
- Follow the pattern: test_[what]_[expected behavior]
- Include the scenario being tested

```python
# Good names:
test_resistor_value_when_changed_updates_properly()
test_schematic_generation_with_two_resistors()

# Bad names:
test_resistor()  # Too vague
test_r1()       # Uninformative
```

## Essential Practices

### 1. Proper Test Isolation
```python
# Good Practice
@pytest.fixture
def temp_project_dir(tmp_path):
    """Create an isolated test directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir

def test_schematic_generation(temp_project_dir):
    # Test uses isolated directory
```

### 2. Comprehensive Error Testing
```python
@pytest.mark.parametrize("invalid_value", [
    "",
    None,
    "Invalid-Value",
])
def test_resistor_invalid_values(invalid_value):
    """Test all invalid value scenarios"""
    with pytest.raises(ValueError):
        Part("Device", "R", value=invalid_value)
```

### 3. Configuration Management
```python
# Good: Use constants and configuration objects
TEST_CONFIG = {
    "resistor": {
        "default_value": "10k",
        "default_footprint": "R_0603_1608Metric",
    }
}

def test_resistor_config():
    r = Part("Device", "R", 
             value=TEST_CONFIG["resistor"]["default_value"])
```

### 4. Helpful Error Messages
```python
# Good: Descriptive assertion messages
assert r_symbol is not None, "Device:R library symbol missing from schematic"
assert value == expected, f"Value mismatch: expected {expected}, got {value}"
```

## Common Pitfalls to Avoid

1. **Hardcoded Paths/Values**
   ```python
   # Bad
   test_file = "/home/user/test.txt"
   
   # Good
   test_file = Path(__file__).parent / "test_data" / "test.txt"
   ```

2. **Missing Edge Cases**
   ```python
   # Incomplete
   def test_resistor_value():
      r = Part("Device", "R", value="10k")
      assert r.value == "10k"
      
   # Better
   @pytest.mark.parametrize("value,expected", [
       ("10k", "10k"),
       ("1M", "1M"),
       (None, ""),
       ("", ""),
   ])
   def test_resistor_value(value, expected):
       r = Part("Device", "R", value=value)
       assert r.value == expected
   ```

3. **Insufficient Setup Documentation**
   ```python
   # Bad
   def test_complex_circuit():
       # Magic numbers and unexplained setup
       
   # Good
   def test_complex_circuit():
       """
       Test circuit generation with the following components:
       - Two resistors in parallel
       - One capacitor for filtering
       - Expected connections documented
       """
   ```

## Testing Complex Systems

### 1. Component Testing
- Test individual components before integration
- Use factory patterns for complex object creation
- Test component interfaces thoroughly

### 2. Integration Points
- Identify and test critical integration points
- Use mocks strategically for external dependencies
- Test error handling at integration boundaries

### 3. System State Validation
```python
def verify_schematic_state(schematic):
    """Verify complete schematic state"""
    errors = []
    if not schematic.components:
        errors.append("No components found")
    if not schematic.connections:
        errors.append("No connections found")
    # ... more checks
    assert not errors, f"Schematic validation failed:\n" + "\n".join(errors)
```

## Best Practices for Fixtures

### 1. Scope Management
```python
@pytest.fixture(scope="session")
def global_config():
    """Configuration used across all tests"""
    return load_test_config()

@pytest.fixture(scope="function")
def temp_circuit(temp_project_dir):
    """Fresh circuit for each test"""
    return Circuit()
```

### 2. Cleanup
```python
@pytest.fixture
def temp_files():
    """Fixture with cleanup"""
    files_created = []
    yield files_created
    # Cleanup after test
    for file in files_created:
        file.unlink()
```

## Testing Tools and Techniques

### 1. Parameterized Testing
```python
@pytest.mark.parametrize("value,footprint", [
    ("10k", "0603"),
    ("1M", "0805"),
    ("100", "1206"),
])
def test_resistor_combinations(value, footprint):
    """Test multiple combinations efficiently"""
```

### 2. Mock Objects
```python
def test_external_dependency(mocker):
    """Test with mocked dependency"""
    mock_lib = mocker.patch('module.external_library')
    mock_lib.return_value = expected_value
    # Test implementation
```

### 3. Test Categories
```python
@pytest.mark.slow
def test_large_circuit():
    """Mark tests for selective running"""

@pytest.mark.integration
def test_system_integration():
    """Integration test marker"""
```

## Continuous Integration Considerations

1. **Test Environment**
   - Document all dependencies
   - Use virtual environments
   - Specify minimum Python version

2. **Test Coverage**
   - Aim for meaningful coverage
   - Focus on critical paths
   - Don't pursue 100% coverage blindly

3. **Performance**
   - Keep unit tests fast
   - Separate slow integration tests
   - Use appropriate test categories

## Lessons Learned from Failed Tests

1. **Symbol Verification**
   - Always verify library symbols exist before testing properties
   - Check symbol definitions match expected format
   - Validate symbol inheritance chain

2. **Error Handling**
   - Verify error conditions trigger expected exceptions
   - Test boundary conditions thoroughly
   - Don't assume error handling behavior

3. **State Management**
   - Clear test state between runs
   - Verify component creation order
   - Check for unintended side effects

## Documentation

1. **Test Documentation**
   - Document test purpose and assumptions
   - Explain complex test setups
   - Document expected behavior changes

2. **Maintenance Notes**
   - Note known limitations
   - Document workarounds
   - Explain test dependencies

## Future Considerations

1. **Scalability**
   - Plan for test suite growth
   - Consider test execution time
   - Implement proper test organization

2. **Maintenance**
   - Regular test review and cleanup
   - Remove obsolete tests
   - Update tests with code changes

Remember: Tests are code too. They deserve the same level of care and maintenance as production code.