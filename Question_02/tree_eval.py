"""
tree_eval.py
============
Rakebun owns this file.
 
Responsibility: Walk a parsed AST and compute a numeric result.
 
This is intentionally separate from the parser so that in future you
could swap in a different back-end (e.g. symbolic simplification, code
generation) without touching the parser.
 
Edge cases handled
------------------
  - Division by zero              → raises ZeroDivisionError
  - Result is a whole number      → returned as float but displayed as int
  - Result rounded to 4 d.p.     → done in evaluator.py, not here (separation
                                    of concerns: this module returns full precision)
  - Unknown AST node kind         → raises ValueError (defensive programming)
  - Overflow / very large numbers → Python floats silently become inf; we detect
                                    and raise ArithmeticError so the caller can
                                    record ERROR instead of "inf"
"""