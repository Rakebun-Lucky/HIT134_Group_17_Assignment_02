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

import math


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate(node: tuple) -> float:
    """
    Recursively evaluate an AST node and return the numeric result.

    Parameters
    ----------
    node : tuple
        An AST node produced by parser_module.parse().
        Valid forms:
          ('NUM',   float)
          ('NEG',   operand_node)
          ('BINOP', op_str, left_node, right_node)

    Returns
    -------
    float
        The computed value at full Python float precision.

    Raises
    ------
    ZeroDivisionError
        When a division by zero is encountered.
    ArithmeticError
        When the result overflows to infinity.
    ValueError
        When an unknown AST node kind is encountered (defensive).

    Examples
    --------
    >>> evaluate(('NUM', 3.0))
    3.0
    >>> evaluate(('BINOP', '+', ('NUM', 3.0), ('NUM', 5.0)))
    8.0
    >>> evaluate(('NEG', ('NUM', 5.0)))
    -5.0
    >>> evaluate(('BINOP', '*', ('NEG', ('NUM', 2.0)), ('NUM', 3.0)))
    -6.0
    """
    kind = node[0]

    # ------------------------------------------------------------------
    # Leaf node – just return the literal value
    # ------------------------------------------------------------------
    if kind == 'NUM':
        return node[1]

    # ------------------------------------------------------------------
    # Unary negation
    # ------------------------------------------------------------------
    if kind == 'NEG':
        return -evaluate(node[1])

    # ------------------------------------------------------------------
    # Binary operation
    # ------------------------------------------------------------------
    if kind == 'BINOP':
        _, op, left_node, right_node = node

        left  = evaluate(left_node)
        right = evaluate(right_node)

        if op == '+':
            result = left + right
        elif op == '-':
            result = left - right
        elif op == '*':
            result = left * right
        elif op == '/':
            # Check for zero before dividing to give a clear error message
            if right == 0:
                raise ZeroDivisionError(
                    f"Division by zero: {left} / {right}"
                )
            result = left / right
        else:
            # Defensive: the parser should never emit an unknown operator
            raise ValueError(f"Unknown operator: {op!r}")

        # Detect overflow (Python float → inf for very large numbers)
        if math.isinf(result):
            raise ArithmeticError(
                f"Arithmetic overflow: result is infinite ({left} {op} {right})"
            )

        return result

    # ------------------------------------------------------------------
    # Unknown node type – should never happen with a well-formed AST
    # ------------------------------------------------------------------
    raise ValueError(f"Unknown AST node kind: {kind!r}")