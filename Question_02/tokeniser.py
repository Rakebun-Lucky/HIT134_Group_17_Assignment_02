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


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def tokenise(text: str) -> list[tuple]:
    """
    Tokenise *text* and return a list of (TYPE, value) tuples ending with END.

    Parameters
    ----------
    text : str
        A single expression string, e.g. "3 + 5 * (2 - -1)".

    Returns
    -------
    list of (str, any)
        Token list, always terminated by ('END', None).

    Raises
    ------
    ValueError
        On any character that is not a digit, decimal point, operator,
        parenthesis, or whitespace.

    Examples
    --------
    >>> tokenise("3 + 5")
    [('NUM', 3.0), ('OP', '+'), ('NUM', 5.0), ('END', None)]
    >>> tokenise("-5")
    [('OP', '-'), ('NUM', 5.0), ('END', None)]
    """
    tokens: list[tuple] = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        # ------------------------------------------------------------------
        # Skip whitespace
        # ------------------------------------------------------------------
        if c in ' \t':
            i += 1
            continue

        # ------------------------------------------------------------------
        # Numeric literal  – greedy scan of digits and at most one dot.
        # Supports:  42   3.14   .5   0.001
        # Does NOT support scientific notation (out of scope).
        # ------------------------------------------------------------------
        if c.isdigit() or (c == '.' and i + 1 < n and text[i + 1].isdigit()):
            j = i
            dot_seen = False

            while j < n and (text[j].isdigit() or (text[j] == '.' and not dot_seen)):
                if text[j] == '.':
                    dot_seen = True
                j += 1

            # Guard: a trailing dot with nothing after it (e.g. "5.") is fine
            # – float() handles it – but two dots would have been stopped by
            # dot_seen above, so no extra check needed.
            raw = text[i:j]
            try:
                tokens.append(('NUM', float(raw)))
            except ValueError:
                raise ValueError(f"Malformed number literal: {repr(raw)}")
            i = j
            continue

        # ------------------------------------------------------------------
        # Operators
        # ------------------------------------------------------------------
        if c in '+-*/':
            tokens.append(('OP', c))
            i += 1
            continue

        # ------------------------------------------------------------------
        # Parentheses
        # ------------------------------------------------------------------
        if c == '(':
            tokens.append(('LPAREN', '('))
            i += 1
            continue

        if c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue

        # ------------------------------------------------------------------
        # Anything else is an error
        # ------------------------------------------------------------------
        raise ValueError(
            f"Unrecognised character {repr(c)} at position {i} in: {repr(text)}"
        )

    # Sentinel so the parser never has to bounds-check the token list.
    tokens.append(('END', None))
    return tokens


def tokens_to_str(tokens: list[tuple]) -> str:
    """
    Format a token list as the required output string.

    Each token is formatted as [TYPE:value], separated by spaces, ending
    with [END].  NUM values that are whole numbers are shown without a
    decimal point to match the expected output (e.g. [NUM:3] not [NUM:3.0]).

    Parameters
    ----------
    tokens : list of (str, any)
        Output of tokenise().

    Returns
    -------
    str
        e.g. "[NUM:3] [OP:+] [NUM:5] [END]"

    Examples
    --------
    >>> tokens_to_str([('NUM', 3.0), ('OP', '+'), ('NUM', 5.0), ('END', None)])
    '[NUM:3] [OP:+] [NUM:5] [END]'
    """
    parts: list[str] = []

    for typ, val in tokens:
        if typ == 'END':
            parts.append('[END]')
        elif typ == 'NUM':
            # Show 3.0 as 3, but keep 3.14 as 3.14
            display = str(int(val)) if val == int(val) else str(val)
            parts.append(f'[NUM:{display}]')
        else:
            # OP, LPAREN, RPAREN
            parts.append(f'[{typ}:{val}]')

    return ' '.join(parts)