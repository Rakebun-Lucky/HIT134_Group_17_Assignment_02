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

from tokeniser import tokenise


# ---------------------------------------------------------------------------
# State helpers – keep parser functions readable
# ---------------------------------------------------------------------------

def _current(state: list) -> tuple:
    """Return the token at the current cursor position (no advance)."""
    tokens, pos = state
    return tokens[pos]


def _advance(state: list) -> tuple:
    """Return the current token and move the cursor forward by one."""
    tokens, pos = state
    state[1] += 1          # mutate pos in place
    return tokens[pos]     # return the token we just consumed


def _expect(state: list, typ: str, val=None) -> tuple:
    """
    Assert the current token matches *typ* (and optionally *val*),
    consume it, and return it.  Raises ValueError if the token doesn't match.
    """
    tok = _current(state)
    if tok[0] != typ or (val is not None and tok[1] != val):
        expected = f"{typ}({val})" if val is not None else typ
        raise ValueError(
            f"Expected {expected} but found {tok[0]}({tok[1]!r})"
        )
    return _advance(state)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(tokens: list[tuple]):
    """
    Parse *tokens* (output of tokenise()) into an AST node.

    Parameters
    ----------
    tokens : list of (str, any)
        Must end with ('END', None).

    Returns
    -------
    tuple
        Root AST node.

    Raises
    ------
    ValueError
        On any syntax error: unexpected token, mismatched parens,
        unary +, empty expression, trailing tokens, etc.

    Examples
    --------
    >>> parse(tokenise("3 + 5"))
    ('BINOP', '+', ('NUM', 3.0), ('NUM', 5.0))
    >>> parse(tokenise("-5"))
    ('NEG', ('NUM', 5.0))
    """
    # Reject blank / whitespace-only input before we even try
    if tokens == [('END', None)]:
        raise ValueError("Empty expression")

    state = [tokens, 0]
    tree = _parse_expression(state)

    # If there are tokens left over the expression was malformed,
    # e.g. "3 + 5 )" — the ')' was never consumed.
    if _current(state)[0] != 'END':
        tok = _current(state)
        raise ValueError(
            f"Unexpected token after expression: {tok[0]}({tok[1]!r})"
        )

    return tree


# ---------------------------------------------------------------------------
# Grammar rule implementations (private)
# ---------------------------------------------------------------------------

def _parse_expression(state: list):
    """
    expression → term ( ('+' | '-') term )*

    Handles addition and subtraction (lowest precedence).
    Builds a left-associative chain:  3 - 2 - 1  →  (- (- 3 2) 1)
    """
    node = _parse_term(state)

    while _current(state)[0] == 'OP' and _current(state)[1] in ('+', '-'):
        op = _advance(state)[1]       # consume '+' or '-'
        right = _parse_term(state)
        node = ('BINOP', op, node, right)

    return node


def _parse_term(state: list):
    """
    term → factor ( ('*' | '/') factor )*

    Handles multiplication and division (medium precedence).
    Also left-associative:  8 / 4 / 2  →  (/ (/ 8 4) 2)
    """
    node = _parse_factor(state)

    while _current(state)[0] == 'OP' and _current(state)[1] in ('*', '/'):
        op = _advance(state)[1]       # consume '*' or '/'
        right = _parse_factor(state)
        node = ('BINOP', op, node, right)

    return node


def _parse_factor(state: list):
    """
    factor → '-' factor
           | primary ( primary )*

    Handles:
      1. Unary minus  – right-recursive so  --5  works:
            NEG → NEG → NUM:5
      2. Unary plus   – explicitly forbidden by the spec.
      3. Implicit multiplication – two adjacent primaries with no operator,
         e.g.  2(3+4)  or  (2+1)(3-1).

    Implicit multiplication is LEFT-associative and has the same precedence
    as explicit '*', which is what most calculators expect.
    """
    tok = _current(state)

    # ------------------------------------------------------------------
    # Case 1: unary minus  →  recurse (right-recursive handles  --5)
    # ------------------------------------------------------------------
    if tok[0] == 'OP' and tok[1] == '-':
        _advance(state)                    # consume '-'
        operand = _parse_factor(state)     # right-recursive
        return ('NEG', operand)

    # ------------------------------------------------------------------
    # Case 2: unary plus — NOT supported per spec
    # ------------------------------------------------------------------
    if tok[0] == 'OP' and tok[1] == '+':
        raise ValueError(
            "Unary '+' is not supported. "
            "Did you mean a binary addition?"
        )

    # ------------------------------------------------------------------
    # Case 3: parse a primary, then check for implicit multiplication
    # ------------------------------------------------------------------
    node = _parse_primary(state)

    # Implicit multiply: if the next token starts a new primary (a number
    # or an opening paren), treat adjacency as multiplication.
    # e.g.  2(3)  →  BINOP('*', NUM:2, NUM:3)
    while _current(state)[0] in ('NUM', 'LPAREN'):
        right = _parse_primary(state)
        node = ('BINOP', '*', node, right)

    return node


def _parse_primary(state: list):
    """
    primary → NUM | '(' expression ')'

    Base cases:
      - A bare number literal.
      - A parenthesised sub-expression (recurses all the way back to
        _parse_expression, which is why nested parens work to any depth).

    Raises ValueError for:
      - A closing paren with no matching open paren.
      - An operator where a value is expected (e.g. "* 5").
      - END reached before the expression is complete.
    """
    tok = _current(state)

    # ------------------------------------------------------------------
    # Numeric literal
    # ------------------------------------------------------------------
    if tok[0] == 'NUM':
        _advance(state)
        return ('NUM', tok[1])

    # ------------------------------------------------------------------
    # Parenthesised sub-expression
    # ------------------------------------------------------------------
    if tok[0] == 'LPAREN':
        _advance(state)                        # consume '('

        # Guard: empty parentheses "()" are not valid
        if _current(state)[0] == 'RPAREN':
            raise ValueError("Empty parentheses '()' are not a valid expression")

        node = _parse_expression(state)        # recurse to top of grammar

        # Consume the closing ')'
        _expect(state, 'RPAREN')
        return node

    # ------------------------------------------------------------------
    # Error cases
    # ------------------------------------------------------------------
    if tok[0] == 'RPAREN':
        raise ValueError("Unexpected ')' – no matching '(' found")

    if tok[0] == 'OP':
        raise ValueError(
            f"Operator {tok[1]!r} found where a value was expected. "
            "If you meant unary minus use '-', unary '+' is not supported."
        )

    if tok[0] == 'END':
        raise ValueError(
            "Expression ended unexpectedly – a value or '(' was expected"
        )

    # Shouldn't reach here, but be explicit
    raise ValueError(f"Unexpected token: {tok[0]}({tok[1]!r})")


# ---------------------------------------------------------------------------
# AST → string  (for the Tree: output line)
# ---------------------------------------------------------------------------

def tree_to_str(node: tuple) -> str:
    """
    Serialise an AST node to its prefix-notation string representation.

    Rules:
      - NUM              →  "3"  (integer if whole, else float)
      - BINOP(op, l, r)  →  "(op left right)"
      - NEG(operand)     →  "(neg operand)"

    Parameters
    ----------
    node : tuple
        An AST node as returned by parse().

    Returns
    -------
    str
        Prefix string, e.g. "(+ 3 (* 5 2))"

    Examples
    --------
    >>> tree_to_str(('BINOP', '+', ('NUM', 3.0), ('NUM', 5.0)))
    '(+ 3 5)'
    >>> tree_to_str(('NEG', ('NUM', 5.0)))
    '(neg 5)'
    """
    kind = node[0]

    if kind == 'NUM':
        v = node[1]
        return str(int(v)) if v == int(v) else str(v)

    if kind == 'BINOP':
        _, op, left, right = node
        return f'({op} {tree_to_str(left)} {tree_to_str(right)})'

    if kind == 'NEG':
        return f'(neg {tree_to_str(node[1])})'

    # Should never happen if parse() only creates the three node types above
    raise ValueError(f"Unknown AST node kind: {kind!r}")