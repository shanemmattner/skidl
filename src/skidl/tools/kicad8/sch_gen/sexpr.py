# src/skidl/tools/kicad8/sch_gen/sexpr.py

from dataclasses import dataclass
from typing import List, Union, Dict, Optional
import re

@dataclass
class SExpr:
    """Represents a parsed s-expression node"""
    token: str
    attributes: List[Union[str, 'SExpr']]
    parent: Optional['SExpr'] = None
    
    def __eq__(self, other):
        if not isinstance(other, SExpr):
            return False
        return (self.token == other.token and 
                len(self.attributes) == len(other.attributes) and
                all(a == b for a, b in zip(self.attributes, other.attributes)))
    
    def find(self, token: str) -> Optional['SExpr']:
        """Find first child node with given token"""
        if self.token == token:
            return self
        for attr in self.attributes:
            if isinstance(attr, SExpr):
                result = attr.find(token)
                if result:
                    return result
        return None

    def get_attribute_value(self, index: int = 0) -> str:
        """Get attribute value, stripping quotes if present"""
        if index >= len(self.attributes):
            return None
        value = self.attributes[index]
        if isinstance(value, str):
            return value.strip('"')
        return value

class SchematicParser:
    """Parser for KiCad schematic files"""
    
    def __init__(self):
        self.normalized_uuids = {}  # Maps real UUIDs to normalized ones
        self.uuid_counter = 0
    
    def _normalize_string(self, s: str) -> str:
        """Normalize a string by stripping quotes"""
        return s.strip('"')
    
    def _tokenize(self, content: str) -> List[str]:
        """Split content into tokens, preserving quoted strings"""
        tokens = []
        current = []
        in_quotes = False
        in_token = False
        
        for char in content:
            if char == '"':
                in_quotes = not in_quotes
                current.append(char)
            elif char.isspace() and not in_quotes:
                if current:
                    tokens.append(''.join(current))
                    current = []
                in_token = False
            elif char == '(':
                if current:
                    tokens.append(''.join(current))
                    current = []
                tokens.append('(')
            elif char == ')':
                if current:
                    tokens.append(''.join(current))
                    current = []
                tokens.append(')')
            else:
                current.append(char)
                in_token = True
                
        if current:
            tokens.append(''.join(current))
            
        return tokens
    
    def _parse_tokens(self, tokens: List[str], index: int = 0) -> tuple[SExpr, int]:
        """Parse tokens into SExpr tree"""
        if index >= len(tokens):
            raise ValueError("Unexpected end of tokens")
            
        if tokens[index] != '(':
            raise ValueError(f"Expected '(' at token {index}: {tokens[index]}")
            
        index += 1
        if index >= len(tokens):
            raise ValueError("Unexpected end of tokens after (")
            
        token = tokens[index]
        attributes = []
        index += 1
        
        while index < len(tokens):
            current = tokens[index]
            
            if current == '(':
                # Nested expression
                nested_expr, new_index = self._parse_tokens(tokens, index)
                nested_expr.parent = None  # Avoid circular references
                attributes.append(nested_expr)
                index = new_index
            elif current == ')':
                # End of current expression
                return SExpr(token, attributes), index + 1
            else:
                attributes.append(current)
                index += 1
                
        raise ValueError("Unclosed s-expression")
    
    def parse(self, content: str) -> SExpr:
        """Parse schematic content into SExpr tree"""
        tokens = self._tokenize(content)
        tree, _ = self._parse_tokens(tokens)
        return tree
    
    def compare(self, content1: str, content2: str) -> bool:
        """Compare two schematic contents ignoring formatting and UUIDs"""
        try:
            tree1 = self.parse(content1)
            tree2 = self.parse(content2)
            return tree1 == tree2
        except ValueError as e:
            print(f"Error parsing schematics: {e}")
            return False

def normalize_schematic(content: str) -> str:
    """Normalize a schematic file for comparison"""
    parser = SchematicParser()
    tree = parser.parse(content)
    return tree.to_sexpr()