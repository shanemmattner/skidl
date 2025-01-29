
# Handling KiCad Symbol Inheritance (`(extends "SomeParentSymbol")`)

This document provides a **detailed plan** for supporting symbol inheritance in a KiCad-based system. The objective is to merge parent (inherited) symbol definitions and child (extending) symbol definitions, **without** any hard-coded references to specific parts. This approach should comfortably handle large libraries with thousands of symbols and *multi-level* inheritance (child-of-child-of-child, etc.).

---

## 1. Detect and Record the Child’s “Extends”

1. **Look for `(extends "SomeParentSymbol")`**  
   While parsing each symbol definition, check if there is an `(extends "...")` property.  
   - If present, store that parent’s name in your internal data structure (e.g., `child_symbol.extends = "AP1117-15"`).  

2. **Consider “Root” Symbols**  
   If `(extends ...)` is **not** present, the symbol is effectively a “root” (no inheritance).  

3. **Avoid Cycles**  
   Validate that the parent’s name is well-formed and does not produce a *cycle*. For example, if A extends B, but B also (directly or indirectly) extends A, handle it (e.g., by raising an error).

---

## 2. Retrieve and Flatten the Parent Symbol (Recursively)

1. **Parse and Cache**  
   - Keep an in-memory cache/dictionary of “flattened” symbols you have already processed.  
   - When you see `(extends "SomeParent")`, check if that parent is already in the **flattened** cache.  
     - If it is not in the cache, **parse and flatten** it now (recursively).  

2. **Multi-Level Inheritance**  
   - If the parent also extends another symbol, apply the same logic.  
   - Eventually, you reach a parent that has no `extends`, i.e., a base or root symbol.  

3. **Store the Flattened Parent**  
   - After fully flattening the parent, store it in `flattened_symbol_cache[parent_name]`.  
   - This speeds up subsequent lookups.

---

## 3. Merge the Parent into the Child

When you finally have the entire, flattened parent definition, combine it with the child’s partial definition:

1. **Merge Properties**  
   - For each property (e.g., `Description`, `Footprint`, `Datasheet`, custom fields, etc.), if the child provides an override, that wins. Otherwise, copy the parent’s property.  
   - If the child sets a property to an empty string, interpret that as removing the parent’s property (if desired).

2. **Merge Pins**  
   - Gather the parent’s pins, then integrate or override child pins.  
   - If the child redefines a pin number that also appears in the parent, the child’s version wins.  
   - If the child adds brand-new pins, simply append them.

3. **Merge Graphics**  
   - In a simple approach, **append** child geometry after the parent’s geometry. The child shapes draw on top.  
   - More advanced systems can detect if the child wants to *replace* or *remove* a specific shape from the parent, but that is optional.

4. **Flatten the Child**  
   - After merging, the child is a single, self-contained symbol.  
   - In your final `.kicad_sch` or `.kicad_sym`, do **not** necessarily keep `(extends ...)`, because you have fully merged the data. If you do want to preserve it for debugging, that is an optional step.

---

## 4. Output the Merged Symbol

Once you have merged, output the child as a **standalone** symbol:

1. **S-Expression**  
   - Use `(symbol "Name" (property "..." ...) (pin ...) (graphics ...))` etc.  
   - Include everything from the flattening process.  

2. **Collision Checks**  
   - If the child redefines the same custom field or pin number, child overrides the parent.  

3. **Final Symbol**  
   - You do not rely on referencing the parent for partial content.  
   - That ensures your final schematic library is fully “expanded.”

4. **Cache the Result**  
   - Store this child’s flattened version in something like `flattened_symbol_cache[child_name]` to handle any future references.

---

## 5. Implementation Tips

- **Data Structures:**  
  You can store each symbol’s parse results in a structure like:
  ```python
  class SymbolDefinition:
      name: str
      extends: Optional[str]
      properties: Dict[str, str]
      pins: List[PinObject]
      graphics: List[GraphicObject]
      ...
  ```
- **Recursive Method:**  
  ```python
  def get_flattened_symbol(symbol_name) -> SymbolDefinition:
      if symbol_name in flattened_symbol_cache:
          return flattened_symbol_cache[symbol_name]
      raw_sym = parse_raw_symbol(symbol_name)
      if raw_sym.extends:
          parent = get_flattened_symbol(raw_sym.extends)
          merged = merge_symbols(parent, raw_sym)
      else:
          merged = raw_sym
      flattened_symbol_cache[symbol_name] = merged
      return merged
  ```
- **Performance:**  
  Because you do not repeatedly parse the same parent symbol, it scales to thousands of parts.  

- **No Hard-Coding:**  
  The logic does **not** rely on special knowledge of “AP1117-15” or “NCP1117-3.3” or any specific part name. All merges happen generically based on `(extends ...)`.

---

## 6. Special Notes on `(extends "...")`

- If your code sees `(extends "AP1117-15")`, it must fetch “AP1117-15”, flatten it if needed, then apply child overrides for “NCP1117-3.3_SOT223.”  
- For multi-level, if “AP1117-15” itself extends “RegulatorBase,” continue up the chain.  
- If you detect cyclical references, fail gracefully.

---

## 7. Summary

By recognizing `(extends "ParentSymbol")`, recursively flattening the parent, and merging into the child, **kicad_writer.py** can produce **fully valid** single-symbol definitions for **all** inherited parts—**without** any hard-coded solutions. The steps:

1. **Parse** `(extends)`.
2. **Flatten** parent.
3. **Merge** child + parent definitions.
4. **Write** final child symbol.

This approach ensures correct symbols for the entire library, including the `NCP1117-3.3_SOT223` that extends `AP1117-15`.
