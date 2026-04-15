"""
parser_module.py
================
Rakebun owns this file.
 
Responsibility: Turn a flat token list into an Abstract Syntax Tree (AST).
 
The parser uses *recursive descent*: one function per grammar rule.
Operator precedence falls out naturally from the call hierarchy —
higher-precedence operations are parsed deeper in the call stack, so
they bind more tightly.
 
Grammar (from lowest to highest precedence):
--------------------------------------------
    expression  →  term   ( ('+' | '-') term   )*
    term        →  factor ( ('*' | '/')  factor )*
    factor      →  '-' factor                        ← unary minus (right-assoc)
                |  primary ( primary )*              ← implicit multiplication
    primary     →  NUM
                |  '(' expression ')'
 
AST node format (plain tuples, no classes):
-------------------------------------------
    ('NUM',    float)               – numeric leaf
    ('BINOP',  op, left, right)     – binary operation; op is '+' '-' '*' '/'
    ('NEG',    operand)             – unary negation
 
Parser state
------------
The mutable list  [tokens, pos]  is threaded through every function.
Using a list (not a tuple) means helper functions can increment pos in
place without returning it.  All parse_* functions receive *state* and
advance the cursor as they consume tokens.
 
Edge cases handled
------------------
  - Unary minus anywhere: -5, --5, -(3+4), 3 * -2
  - Unary plus is explicitly rejected with a clear error message.
  - Implicit multiplication: 2(3+4), (2+1)(3-1), 3(4)
  - Deeply nested parentheses: (((3)))
  - Mismatched parentheses: (3+5  or  3+5)
  - Trailing garbage after a valid expression: "3 + 5 )"
  - Empty input / blank line.
  - Division by zero detected at evaluation time (see tree_eval.py).
"""