# KiCad Schematic Generation Troubleshooting Guide

## Detailed Error Analysis: UnboundLocalError with Schematic Class

### Potential Root Causes

1. **Scope Conflict**
   - Multiple imports of `Schematic` in different scopes
   - Local function-level import shadowing global import

2. **Library Compatibility**
   - Version mismatch between kiutils and current implementation
   - Unexpected changes in library API

3. **Import Mechanism**
   - Potential issues with Python's import system in this specific context

### Diagnostic Checklist

#### 1. Import Verification
- Confirm kiutils library version: `pip show kiutils`
- Verify import statement: `from kiutils.schematic import Schematic`
- Check for any circular or conflicting imports

#### 2. Error Handling Strategy
```python
try:
    # Explicit error handling
    main_sch = Schematic.from_file(main_sch_path)
except Exception as e:
    print(f"Schematic loading error: {type(e).__name__} - {e}")
    # Fallback mechanism
    main_sch = Schematic.create_new()
```

#### 3. Debugging Techniques
- Add verbose logging
- Print import paths
- Verify library installation
- Check Python environment

### Recommended Fixes

1. **Consistent Global Import**
   ```python
   # At top of file
   from kiutils.schematic import Schematic
   
   # Remove local imports inside functions
   ```

2. **Robust Schematic Creation**
   ```python
   def safe_schematic_load(file_path):
       try:
           return Schematic.from_file(file_path)
       except Exception as load_error:
           print(f"Schematic load failed: {load_error}")
           return Schematic.create_new()
   ```

### Environment Diagnostics

To help diagnose the issue, collect the following information:
- Python version
- kiutils version
- Full error traceback
- Exact import statements
- Context of schematic generation

### Potential Workarounds
- Manually create minimal schematic
- Use alternative schematic generation method
- Update kiutils library