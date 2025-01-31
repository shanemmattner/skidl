# Handling KiCad Symbol Inheritance (`(extends "SomeParentSymbol")`)

This document captures **all** important details, *attempts*, and *changes* discussed in this chat regarding flattening KiCad symbols that use `(extends "...")`. We have tried multiple approaches to:

1. **Parse** each `(symbol "Child" (extends "Parent") ...)`.
2. **Recursively** flatten the entire inheritance chain (child → parent → parent's parent → etc.).
3. **Merge** the parent’s pins, properties, shapes, and other data into the child.
4. **Remove** `(extends ...)` from the final, expanded `(symbol ...)` definition.

Despite code tries, we encountered issues with indentation, bracket structure, or raw text splicing. Below is an **all-inclusive** summary of how to implement a robust solution, plus a record of what was tried and why.

---

## **Chat History and Summary of Attempts**

- Initially, the project was using **raw text splicing**:  
  1. Grab the child `(symbol "Foo" (extends "Bar") ...)` lines.  
  2. Insert them above the parent’s final `)`.  
  This fails because it never truly merges pins, properties, or geometry. It can also produce malformed s-expressions.

- We then tried a **structured parse** (using a `SymbolDefinition` object) plus a simple `_prettify_sexpr()` function that re-indents the final lines. Some incomplete or mismatched parentheses in the shapes block still led to incorrect indentation.

- We introduced code that fully flattens the data, then re-builds each `(symbol ...)` from scratch. This approach is correct in principle, but we had to handle careful bracket/indentation for shapes, pins, and properties. Additional complexity arises if the library symbol lines contain partial shapes spread across multiple lines.

- The final code attempts included:
  1. **`symbol_parser.py`:** A structured parser for `(symbol "X" ...)`, storing `extends`, `properties`, `pins`, `raw_shapes`, then merging them.  
  2. **`kicad_writer.py`:** A `KicadSchematicWriter` that calls the parser, flattens each symbol, then writes a big `(lib_symbols ... )` block.  
  3. **`_prettify_sexpr()`** logic to re-indicate the final lines by counting open/close parentheses line by line.

- The result sometimes had incorrectly nested lines in shapes (e.g., `(at X Y Z)` lines merging with `(pin ...)` lines). This yields a “non-functional” s-expression when read by KiCad.

**We discovered that** if the raw library symbols store geometry with multiple lines or partial lines, our naive string approach may break it. A truly robust solution requires a *full s-expression parser* for shapes as well, then re-output those shapes carefully.

---

## **High-Level Steps for a Correct Implementation**

Below is the stable approach that has been **repeatedly** recommended and proven in other contexts:

1. **Parse** each symbol’s entire s-expression:
   - Instead of just “line-based searching,” use a small s-expression library or manual bracket-based parse to build a tree.
   - E.g., parse the child’s `(symbol ... )` into nested data: properties, pins, shapes, etc.
2. **Recursively Flatten**:
   - If `(extends "Parent")`, call `get_flattened_symbol("Parent")`.
   - Merge the parent data into the child, field by field:
     - Parent’s pins are appended, unless the child overrides them by `pin number`.
     - Parent’s shapes are appended below the child’s shapes or used unless overridden.
     - Parent’s `(property "Foo")` are only copied if the child lacks them.
3. **Rebuild** the final `(symbol "Child" ...)`:
   - The final object has all data from parent + child. It has **no** `(extends ...)`.
   - Write it as properly bracketed s-expression:
     ```lisp
     (symbol "ChildName"
       (property "Reference" "U")
       (property "Value" "ChildValue")
       (pin "1" ...)
       (rectangle
         (start ...)
         (end ...)
       )
       ...
     )
     ```
4. **Pretty-Print** the final s-expression tree:
   - Count parentheses and indent accordingly or do a tree-based walker.

**Key detail**: If the library has advanced multi-line shapes, your parser must handle those shapes as sub-trees so you can reassemble them without losing track of parentheses. Doing “line-based” merges or partial string splitting can produce mismatched bracket blocks.

---

## **In-Depth Merging Plan**

### 1) Detect `(extends "...")`
- While parsing `(symbol "X" ...)`, if the top line or any sub-token says `(extends "Parent")`, store `symbol.extends = "Parent"`.

### 2) Flatten Recursively
- Keep a `flattened_cache`. If you flatten “Parent”, store it. 
- Flattening the child:
  1. If child is already “is_flattened = True”, return it.
  2. If child.extends is not `None`, flatten the parent, then `merge_symbol_defs(parent, child)`.
  3. Mark child flattened.

### 3) Merging
- `child.properties[k] = v` if child doesn’t have the property `k`.
- For pins, if `child` has no pin with the same `number`, then copy from parent. If a child pin duplicates, child wins.
- For shapes, append parent’s shapes first, then child’s shapes. (Or do something more advanced if you want child to override certain shapes.)

### 4) Final Output
- Build an s-expression:
  ```python
  (symbol "X"
    (property "Reference" "U")
    ...
    (pin "1")
    ...
  )
  ```
- Use a real bracket-based indentation method to ensure each sub-block is aligned. Doing a line-based approach can work, but only if you have matched parentheses for shapes, properties, etc. If the shapes themselves contain multiple lines with bracket imbalance, do a sub-parse.

---

## **What Has Been Tried in This Chat**

1. **Naive Text Splice** – fails to handle partial shapes or child overriding.  
2. **SymbolParser** storing each symbol’s lines, plus `(extends ...)`. We do `_merge_symbol_defs(...)`, then attempt `_prettify_sexpr()`. We still risk malformed text if sub-blocks in shapes get jumbled.  
3. **Adding bracket counting** to each line. This helps a bit, but if shapes or properties are “semi-split” across lines, you can end up with partial bracket lines out of order.  

**Result**: We got partially correct merges, but indentation or bracket structure sometimes ended up invalid. The final code snippet included `_prettify_sexpr()` in an attempt to fix multiline shapes. In some user tests, KiCad complained that the output was not parseable.

Hence, we either:
- Expand the parser so each shape is *fully parsed into a sub-tree*, or
- For each shape line, store them exactly as-is but keep them within a single bracket block. Then re-output them with correct indentation.

---

## **Conclusion and Next Steps**

**To reliably produce functional code** for all library shapes:

- **Full S-expression Tree**: Instead of partially parsing lines in `(raw_shapes)`, parse every bracket in shapes. This yields a nested AST you can re-serialize with perfect bracket matching.
- **Reserialize** the entire symbol from that AST. Then *no line merges* will break parentheses.  

Short of that, if your library’s shapes are fairly simple (like single-line arcs or rectangles), your existing partial approach might suffice. But advanced or multiline geometry is more likely to produce non-functional code.

**Therefore**, the core recommendation remains:

1. Implement a robust *S-expression parser* for each `(pin ...)`, `(rectangle ...)`, `(arc ...)`, etc.  
2. Merge parent → child in structured objects.  
3. Output a brand new `(symbol ...)` by walking that object tree.  
4. Indent properly by counting open vs. close parentheses from the newly constructed s-expression.

**This** is how you ensure large or multi-level inherited symbols generate correct flattened results, *without* bracket mismatch or indentation trouble.

---

## **Document Outline**

- [Handling KiCad Symbol Inheritance (`(extends "SomeParentSymbol")`)](#handling-kicad-symbol-inheritance-extends-someparentsymbol)
  - [**Chat History and Summary of Attempts**](#chat-history-and-summary-of-attempts)
  - [**High-Level Steps for a Correct Implementation**](#high-level-steps-for-a-correct-implementation)
  - [**In-Depth Merging Plan**](#in-depth-merging-plan)
    - [1) Detect `(extends "...")`](#1-detect-extends-)
    - [2) Flatten Recursively](#2-flatten-recursively)
    - [3) Merging](#3-merging)
    - [4) Final Output](#4-final-output)
  - [**What Has Been Tried in This Chat**](#what-has-been-tried-in-this-chat)
  - [**Conclusion and Next Steps**](#conclusion-and-next-steps)
  - [**Document Outline**](#document-outline)

**All** attempts in this chat revolve around implementing these steps in a partial parser vs. a complete AST. This doc captures the final recommended approach: a *complete parse* + flatten + re-serialize = guaranteed correctness.

