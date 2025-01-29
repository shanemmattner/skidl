#!/usr/bin/env python3
"""
kicad_sym_parser.py

A robust token-based parser for KiCad .kicad_sym symbol library files using
the documented s-expression format. This code can parse:

- The top-level (kicad_symbol_lib ...) header
- Each (symbol "Name" [...]) block
- Sub-blocks like (property ...), (pin ...), and simple shape definitions
- 'extends' references

After parsing, you can flatten multi-level inheritance by referencing
SymbolDefinition.extends and recursively merging.

Usage:
    symbols = parse_kicad_sym("my_library.kicad_sym")
    # symbols is a dict of {symbol_name: SymbolDefinition}, each with pins, properties, shapes...
"""

import re
import uuid
from typing import Dict, List, Union, Optional


###############################################################################
# DATA STRUCTURES
###############################################################################

class SymbolDefinition:
    """
    Represents a single top-level or sub-symbol in a .kicad_sym library.
    Typically top-level symbols have a "LIBRARY_ID" string.
    If the symbol extends a parent, extends = "ParentSymbolName".
    """
    def __init__(self, name: str):
        self.name: str = name
        self.extends: Optional[str] = None
        self.properties: Dict[str, str] = {}
        self.pins: List["PinDefinition"] = []
        self.shapes: List["ShapeDefinition"] = []  # arcs, circles, polygons, etc.

class PinDefinition:
    """Stores minimal info about a pin from (pin ELECTRICAL GRAPHIC (at x y angle) ...)"""
    def __init__(self):
        self.pin_type: str = "passive"     # e.g. 'input', 'output', 'power_in', etc.
        self.pin_shape: str = "line"       # e.g. 'line', 'inverted', etc.
        self.x: float = 0.0
        self.y: float = 0.0
        self.angle: float = 0.0
        self.length: float = 1.27         # default length in mm
        self.name: str = ""
        self.number: str = ""

class ShapeDefinition:
    """
    Generic container for one shape: e.g. (arc ...), (rectangle ...), etc.
    We'll store the raw parse tree or a simplified object.
    """
    def __init__(self, shape_type: str):
        self.shape_type: str = shape_type
        self.attributes: Dict[str, Union[float, str]] = {}
        self.points: List[float] = []  # e.g. for polyline


###############################################################################
# LEXER
###############################################################################

class TokenType:
    # We define a simple set of token types
    LPAREN = "LPAREN"       # (
    RPAREN = "RPAREN"       # )
    SYMBOL = "SYMBOL"       # e.g. extends, pin, property, numeric, yes/no, ...
    STRING = "STRING"       # "some quoted text"
    EOF = "EOF"             # end of file


class Token:
    """Represents a single lexical token from the .kicad_sym file."""
    def __init__(self, ttype: str, value: str, line: int, col: int):
        self.ttype = ttype
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.ttype},{self.value},line={self.line},col={self.col})"


class KiCadSymLexer:
    """
    Splits .kicad_sym text into tokens:
    - '(' => LPAREN
    - ')' => RPAREN
    - Double-quoted "strings" => STRING
    - everything else => SYMBOL
    This handles basic s-expression tokenizing.
    """

    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.col = 1
        self.length = len(text)

    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.ttype == TokenType.EOF:
                break
        return tokens

    def _next_token(self) -> Token:
        # skip whitespace
        self._skip_whitespace_and_comments()

        if self.position >= self.length:
            return Token(TokenType.EOF, "", self.line, self.col)

        ch = self.text[self.position]

        if ch == '(':
            return self._make_simple_token(TokenType.LPAREN, ch)
        if ch == ')':
            return self._make_simple_token(TokenType.RPAREN, ch)
        if ch == '"':
            return self._string_token()
        # else parse a symbol until whitespace or paren
        return self._symbol_token()

    def _skip_whitespace_and_comments(self):
        while self.position < self.length:
            c = self.text[self.position]
            if c in [' ', '\t', '\r', '\n']:
                self._advance()
            # KiCad DSN style comments can be semicolon-based or #, or not?
            # The doc doesn't mention line comments. We'll assume no line comments
            else:
                break

    def _advance(self):
        c = self.text[self.position]
        self.position += 1
        if c == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1

    def _make_simple_token(self, ttype: str, ch: str) -> Token:
        line, col = self.line, self.col
        self._advance()
        return Token(ttype, ch, line, col)

    def _string_token(self) -> Token:
        # consume initial '"'
        line, col = self.line, self.col
        self._advance()  # skip "

        start_pos = self.position
        value_chars = []
        while self.position < self.length:
            c = self.text[self.position]
            if c == '"':
                # end of string
                break
            elif c == '\\':
                # handle escapes for " or \n?
                if self.position + 1 < self.length:
                    nxt = self.text[self.position + 1]
                    if nxt == '"' or nxt == '\\':
                        value_chars.append(nxt)
                        self._advance()
                    else:
                        # basic fallback
                        value_chars.append(c)
                else:
                    value_chars.append(c)
            else:
                value_chars.append(c)
            self._advance()

        # now we must see a closing "
        if self.position >= self.length:
            # unclosed quote
            return Token(TokenType.STRING, "".join(value_chars), line, col)
        # skip the final '"'
        self._advance()

        string_value = "".join(value_chars)
        return Token(TokenType.STRING, string_value, line, col)

    def _symbol_token(self) -> Token:
        line, col = self.line, self.col
        start_pos = self.position
        buf = []
        while self.position < self.length:
            c = self.text[self.position]
            if c in [' ', '\t', '\r', '\n', '(', ')', '"']:
                break
            buf.append(c)
            self._advance()

        val = "".join(buf)
        return Token(TokenType.SYMBOL, val, line, col)


###############################################################################
# PARSER: Build S-expression tree
###############################################################################

class SExprNode:
    """
    Represents a node in the parse tree. Each node can be:
      - SExprNode(list_of_children)
      - or a Leaf node with type=SYMBOL or STRING
    We'll store them as (is_atom, value) for leaves, or (is_atom=False, children=[]) for sub-lists.
    """
    def __init__(self, is_atom: bool, value: str = "", children: List["SExprNode"] = None):
        self.is_atom = is_atom
        self.value = value
        self.children = children if children is not None else []

    def __repr__(self):
        if self.is_atom:
            return f"Atom({self.value})"
        else:
            return f"SExpr({self.children})"


class SExprParser:
    """
    A simple s-expression parser producing a tree of SExprNode objects.
    Grammar:
        sexpr -> '(' {sexpr | atom} ')'
        atom -> SYMBOL | STRING
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.length = len(tokens)

    def parse_toplevel(self) -> List[SExprNode]:
        """
        Parse the entire token stream into a list of top-level expressions.
        Usually, .kicad_sym has (kicad_symbol_lib ... ) as top-level.
        """
        result = []
        while not self._match(TokenType.EOF):
            node = self._parse_expr()
            if node:
                result.append(node)
        return result

    def _parse_expr(self) -> Optional[SExprNode]:
        """Parse a single s-expression or atom, or return None if we see EOF."""
        if self._match(TokenType.EOF):
            return None
        if self._check(TokenType.LPAREN):
            return self._parse_list()
        else:
            # parse an atom
            tok = self._advance()
            if tok.ttype in (TokenType.SYMBOL, TokenType.STRING):
                return SExprNode(is_atom=True, value=tok.value)
            else:
                # error or skip
                return None

    def _parse_list(self) -> Optional[SExprNode]:
        """Parse a '(' expr* ')' block"""
        # consume '('
        self._consume(TokenType.LPAREN, "Expected '('")
        children = []
        while not self._check(TokenType.RPAREN) and not self._check(TokenType.EOF):
            if self._check(TokenType.LPAREN):
                sub = self._parse_list()
                if sub:
                    children.append(sub)
            elif self._check_any([TokenType.SYMBOL, TokenType.STRING]):
                atom_tok = self._advance()
                children.append(SExprNode(is_atom=True, value=atom_tok.value))
            else:
                # might be invalid
                break
        self._consume(TokenType.RPAREN, "Expected ')' to close s-expression")
        return SExprNode(is_atom=False, children=children)

    # utility
    def _check(self, ttype: str) -> bool:
        if self.position >= self.length:
            return False
        return (self.tokens[self.position].ttype == ttype)

    def _check_any(self, ttypes: List[str]) -> bool:
        if self.position >= self.length:
            return False
        return (self.tokens[self.position].ttype in ttypes)

    def _match(self, ttype: str) -> bool:
        if self._check(ttype):
            return True
        return False

    def _advance(self) -> Token:
        if self.position < self.length:
            t = self.tokens[self.position]
            self.position += 1
            return t
        # return a dummy EOF if out of range
        return Token(TokenType.EOF, "", 0,0)

    def _consume(self, ttype: str, msg: str):
        if self._match(ttype):
            return self._advance()
        # else error
        raise ValueError(f"{msg} at token {self.tokens[self.position]}")


###############################################################################
# INTERPRETING THE PARSE TREE FOR .kicad_sym
###############################################################################

def parse_kicad_sym(filename: str) -> Dict[str, SymbolDefinition]:
    """
    Read the file, tokenize it, parse into s-expression trees, then interpret
    the parse trees to produce a dictionary of {symbolName: SymbolDefinition}.
    """
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    lexer = KiCadSymLexer(text)
    tokens = lexer.tokenize()
    parser = SExprParser(tokens)
    toplevel = parser.parse_toplevel()

    # Typically the file structure is (kicad_symbol_lib (version ...) ... (symbol "Foo" ...) (symbol "Bar" ...))
    # We'll find each top-level node. If it's an s-expression with "kicad_symbol_lib" as the first child,
    # interpret that block. Otherwise handle older style. We'll do a minimal approach:
    symbols = {}
    for node in toplevel:
        if node.is_atom:
            continue
        # node is SExpr
        if len(node.children) == 0:
            continue
        # check if first child is an atom named "kicad_symbol_lib"
        first = node.children[0]
        if first.is_atom and first.value == "kicad_symbol_lib":
            # parse inside
            _parse_kicad_symbol_lib(node, symbols)
        elif first.is_atom and first.value == "symbol":
            # top-level symbol
            sym_def = _parse_symbol(node)
            if sym_def:
                symbols[sym_def.name] = sym_def
        # else ignore

    return symbols


def _parse_kicad_symbol_lib(lib_node: SExprNode, symbols_dict: Dict[str, SymbolDefinition]):
    """
    Interprets a (kicad_symbol_lib ... ) node. Inside, we might see (symbol "..." ...) blocks.
    """
    # children of lib_node[1..end] are sub-nodes. Each might be (symbol ...) or (generator ...) etc.
    for child in lib_node.children[1:]:
        if child.is_atom:
            continue
        if len(child.children) < 1:
            continue
        if child.children[0].is_atom and child.children[0].value == "symbol":
            sym_def = _parse_symbol(child)
            if sym_def:
                symbols_dict[sym_def.name] = sym_def


def _parse_symbol(sym_node: SExprNode) -> Optional[SymbolDefinition]:
    """
    Parse a (symbol "Name" ...) node:
        (symbol "Name"
          (extends "ParentName")
          (pin_numbers hide)
          (property "Value" "Foo" ...)
          (pin power_in line ...)
          ...
        )
    We'll extract the 'name', 'extends', plus parse pins, properties, etc.
    """
    # first child: "symbol"
    if len(sym_node.children) < 2:
        return None
    # second child is an atom or string with the symbol name
    name_node = sym_node.children[1]
    if not name_node.is_atom:
        return None
    sym_name = name_node.value
    sym_def = SymbolDefinition(sym_name)

    # parse the rest
    idx = 2
    while idx < len(sym_node.children):
        item = sym_node.children[idx]
        idx += 1
        if item.is_atom:
            # could be 'pin_numbers' or 'pin_names' or 'in_bom' or 'on_board' ...
            # e.g. (pin_numbers hide)
            # but we do not have sub-children -> we can't do much
            pass
        else:
            # item is sub-s-expression, like (extends "Foo"), (property ...), (pin ...), etc.
            if len(item.children) == 0:
                continue
            head = item.children[0]
            if not head.is_atom:
                continue
            head_val = head.value
            if head_val == "extends":
                # e.g. (extends "ParentName")
                if len(item.children) >= 2 and item.children[1].is_atom:
                    sym_def.extends = item.children[1].value
            elif head_val == "property":
                _parse_symbol_property(item, sym_def)
            elif head_val == "pin":
                p = _parse_symbol_pin(item)
                if p:
                    sym_def.pins.append(p)
            elif head_val in ("arc", "circle", "rectangle", "polyline", "bezier"):
                sh = _parse_shape(item, head_val)
                if sh:
                    sym_def.shapes.append(sh)
            # else ignore or handle other sub-blocks

    return sym_def


def _parse_symbol_property(prop_node: SExprNode, sym_def: SymbolDefinition):
    """
    E.g. (property "Value" "SomeVal" (id 1) (at 0 0 0) ...)
    We'll store in sym_def.properties["Value"] = "SomeVal"
    """
    # prop_node.children = [Atom(property), Atom("KEY"), Atom("VALUE"), ...]
    if len(prop_node.children) < 3:
        return
    key_node = prop_node.children[1]
    val_node = prop_node.children[2]
    if not (key_node.is_atom and val_node.is_atom):
        return
    key = key_node.value
    val = val_node.value
    sym_def.properties[key] = val


def _parse_symbol_pin(pin_node: SExprNode) -> Optional[PinDefinition]:
    """
    e.g. (pin input line (at 0 0 0) (length 2.54) (name "GND") (number "1"))
    """
    p = PinDefinition()
    # pin_node.children might be [Atom(pin), Atom(input), Atom(line), SExpr(at ...), SExpr(length ...), SExpr(name "..."), SExpr(number "...")]
    idx = 1
    while idx < len(pin_node.children):
        child = pin_node.children[idx]
        idx += 1
        if child.is_atom:
            # e.g. 'input' or 'line'
            if p.pin_type == "passive":
                p.pin_type = child.value
            else:
                p.pin_shape = child.value
        else:
            # sub-s-expression: e.g. (at 10 20 180), (length 2.54), (name "SDA" ...), (number "5" ...)
            if len(child.children) < 1:
                continue
            c0 = child.children[0]
            if not c0.is_atom:
                continue
            if c0.value == "at":
                # e.g. (at x y angle)
                if len(child.children) >= 2:
                    px = child.children[1]
                    if px.is_atom:
                        p.x = _try_float(px.value)
                if len(child.children) >= 3:
                    py = child.children[2]
                    if py.is_atom:
                        p.y = _try_float(py.value)
                if len(child.children) >= 4:
                    ang = child.children[3]
                    if ang.is_atom:
                        p.angle = _try_float(ang.value)
            elif c0.value == "length":
                if len(child.children) >= 2 and child.children[1].is_atom:
                    p.length = _try_float(child.children[1].value)
            elif c0.value == "name":
                # e.g. (name "SDA" (effects ...))
                if len(child.children) >= 2 and child.children[1].is_atom:
                    p.name = child.children[1].value
            elif c0.value == "number":
                if len(child.children) >= 2 and child.children[1].is_atom:
                    p.number = child.children[1].value
    return p


def _parse_shape(shape_node: SExprNode, shape_type: str) -> Optional[ShapeDefinition]:
    """
    e.g. (arc (start x y) (mid x y) (end x y) (stroke ...) (fill ...))
    We'll do a partial parse to store in a generic shape object.
    """
    sh = ShapeDefinition(shape_type)
    # We can iterate the sub-nodes. For example:
    # shape_node.children = [Atom(arc), SExpr(start x y), SExpr(mid x y), ...]
    idx = 1
    while idx < len(shape_node.children):
        c = shape_node.children[idx]
        idx += 1
        if c.is_atom:
            # do nothing for now
            pass
        else:
            # e.g. (start 10 20)
            if len(c.children) < 1:
                continue
            head = c.children[0]
            if not head.is_atom:
                continue
            cmd = head.value
            if cmd in ("start","mid","end","center","radius"):
                # handle them
                if len(c.children) >= 2 and c.children[1].is_atom:
                    x = _try_float(c.children[1].value)
                    if len(c.children) >= 3 and c.children[2].is_atom:
                        y = _try_float(c.children[2].value)
                    else:
                        y = 0.0
                    # store
                    key = cmd + "_x"
                    sh.attributes[key] = x
                    key2 = cmd + "_y"
                    sh.attributes[key2] = y
            elif cmd == "stroke":
                # parse stroke sub-block
                pass
            elif cmd == "fill":
                pass
            elif cmd == "pts":
                # e.g. (pts (xy x y) (xy x y) ...)
                for pt_expr in c.children[1:]:
                    if len(pt_expr.children) == 3 and pt_expr.children[0].is_atom and pt_expr.children[0].value == "xy":
                        sx = pt_expr.children[1]
                        sy = pt_expr.children[2]
                        sh.points.append(_try_float(sx.value))
                        sh.points.append(_try_float(sy.value))

    return sh


def _try_float(s: str) -> float:
    try:
        return float(s)
    except:
        return 0.0

# end parse_kicad_sym
