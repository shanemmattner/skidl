# KiCad Project File Testing Architecture

## Overview
The schematic generation tests need to verify proper KiCad project file (.kicad_pro) generation to ensure complete and valid KiCad projects.

## Test Requirements

### Project File Existence and Naming
- Verify the .kicad_pro file is generated in the correct project directory
- Check file naming matches project name pattern
- Ensure both main project file and any backup files are properly placed

### Required Structure
The .kicad_pro file must contain these key sections:

1. Meta Section
```json
"meta": {
  "filename": "<project_name>.kicad_pro",
  "version": 1
}
```

2. Sheets Section
```json
"sheets": [
  {
    "path": "<project_name>.kicad_sch",
    "sheet_name": "",
    "id": "<uuid>"
  },
  {
    "path": "<project_name>_circuit.kicad_sch", 
    "sheet_name": "<circuit_name>",
    "id": "<uuid>"
  }
]
```

3. Required Configuration Sections
- board: Contains board-specific settings
- libraries: Symbol and footprint library configurations
- net_settings: Network and class definitions
- pcbnew: PCB editor settings
- schematic: Schematic editor settings
- erc: Electrical rules configuration

### Test Cases

1. Basic Project Structure Test
- Generate project with different directory and project names
- Verify kicad_pro file exists and has correct name
- Check meta section version and filename
- Validate presence of all required sections

2. Sheet Configuration Test  
- Verify sheets section lists all generated schematic files
- Check sheet names and paths match actual files
- Validate sheet IDs are valid UUIDs

3. Default Settings Test
- Verify default net class is configured
- Check ERC rules are properly set
- Validate design rules have reasonable defaults

### Implementation Strategy

1. Project Generation
```python
generate_schematic(
    filepath="test_project_alpha",  # Different directory name
    project_name="beta",           # Different project name
    title="Test Project Beta"
)
```

2. File Verification
```python
# Check project file exists
project_file = project_dir / "beta.kicad_pro"
assert project_file.exists()

# Parse JSON content
with open(project_file) as f:
    project_data = json.loads(f.read())

# Verify structure
assert "meta" in project_data
assert project_data["meta"]["version"] == 1
assert project_data["meta"]["filename"] == "beta.kicad_pro"

# Verify sheets
assert len(project_data["sheets"]) == 2
assert project_data["sheets"][0]["path"] == "beta.kicad_sch"
assert project_data["sheets"][1]["path"] == "beta_circuit.kicad_sch"
```

This ensures the generated KiCad project is complete and properly structured for KiCad to open and edit the project.