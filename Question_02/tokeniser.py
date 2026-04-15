"""
tokeniser.py
============
Chepngenoh owns this file.
 
Responsibility: Convert a raw expression string into a flat list of typed tokens.
 
Token format: (TYPE, value)
  - ('NUM',    float)   – a numeric literal, e.g. 3, 3.14, .5
  - ('OP',     str)     – one of  + - * /
  - ('LPAREN', '(')
  - ('RPAREN', ')')
  - ('END',    None)    – sentinel appended after the last real token
 
Design notes:
  - Unary minus is NOT folded into the number here; -5 produces
    [OP:-][NUM:5] so the parser can distinguish unary from binary minus.
  - Whitespace (spaces and tabs) is silently skipped.
  - Any unrecognised character raises ValueError immediately.
"""