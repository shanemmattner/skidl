# KiCad File Handling Guidelines

## KiCad Symbol Files (.kicad_sym)

### Important Note
KiCad symbol library files (.kicad_sym) should NEVER be read directly using tools like `read_file`. These files are typically very large and can cause performance issues or system hangs when attempting to read them.

### Best Practices
- Do not attempt to read .kicad_sym files directly
- If symbol information is needed, use KiCad's API or specialized tools designed for handling these files
- Consider extracting only the specific symbol information needed rather than processing the entire file

### Alternative Approaches
- Use KiCad's Python API for accessing symbol information
- Extract specific symbols to individual files if needed
- Use specialized parsers designed for handling KiCad library files efficiently