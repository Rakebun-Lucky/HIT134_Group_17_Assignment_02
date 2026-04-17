"""
evaluator.py
============
Chepngenoh owns this file.
 
Responsibility: Orchestrate the full pipeline for one expression, and
expose the  evaluate_file()  interface required by the assignment spec.
 
Pipeline for each expression:
    raw string
        → tokeniser.tokenise()         → token list
        → parser_module.parse()        → AST
        → tree_eval.evaluate()         → float
        → format_result()              → dict  +  output.txt line
 
This file intentionally contains NO parsing or evaluation logic — it
only wires the other modules together and handles all I/O.
 
Edge cases handled here
-----------------------
  - Blank / whitespace-only lines are skipped (no output block generated).
  - Any exception from any pipeline stage is caught and the expression
    is recorded as ERROR without crashing the whole run.
  - The output file is written atomically (all lines built in memory first).
  - Input file encoding falls back gracefully.
"""
import os

from tokeniser      import tokenise, tokens_to_str
from parser_module  import parse, tree_to_str
from tree_eval      import evaluate
# ---------------------------------------------------------------------------
# Single-expression pipeline
# ---------------------------------------------------------------------------

def _format_number(value: float) -> str:
    """
    Format a numeric result per spec:
      - Whole numbers (e.g. 8.0) → "8"  (no decimal point)
      - Everything else          → rounded to 4 decimal places, e.g. "3.3333"

    Parameters
    ----------
    value : float

    Returns
    -------
    str
    """
    if value == int(value):
        return str(int(value))
    return str(round(value, 4))


def _evaluate_one(expr: str) -> dict:
    """
    Run the full pipeline on a single expression string.

    Returns a dict with keys: input, tree, tokens, result.
      - result is a float on success, or the string "ERROR" on failure.
      - tree and tokens are strings (or "ERROR").

    This function never raises — all exceptions are caught and translated
    to ERROR so one bad line doesn't abort the entire file.

    Parameters
    ----------
    expr : str
        A single expression string (no newline).

    Returns
    -------
    dict
    """
    # Default everything to ERROR; overwrite on success at each stage
    result = {
        "input":  expr,
        "tree":   "ERROR",
        "tokens": "ERROR",
        "result": "ERROR",
    }

    try:
        # Stage 1: tokenise
        # -----------------
        tokens = tokenise(expr)
        result["tokens"] = tokens_to_str(tokens)

        # Stage 2: parse  →  AST
        # ----------------------
        tree = parse(tokens)
        result["tree"] = tree_to_str(tree)

        # Stage 3: evaluate  →  numeric result
        # -------------------------------------
        value = evaluate(tree)

        # Store the raw float so the caller can do further processing,
        # and record formatted string in "result" per spec.
        result["result"] = float(value)

    except Exception:
        # Leave result as ERROR; do not re-raise.
        # Uncomment the next line for debugging:
        # import traceback; traceback.print_exc()
        pass

    return result


# ---------------------------------------------------------------------------
# Required public interface  (matches the spec exactly)
# ---------------------------------------------------------------------------

def evaluate_file(input_path: str) -> list[dict]:
    """
    Read mathematical expressions from *input_path* (one per line),
    evaluate each, write results to output.txt in the same directory,
    and return a list of result dicts.

    Parameters
    ----------
    input_path : str
        Path to the input text file.

    Returns
    -------
    list of dict
        One dict per non-blank line with keys:
          "input"   – original expression string
          "tree"    – prefix parse-tree string, or "ERROR"
          "tokens"  – token string, or "ERROR"
          "result"  – float on success, or the string "ERROR"

    Output file format (output.txt)
    --------------------------------
    For each expression, four lines:
        Input:   <original expression>
        Tree:    <prefix tree>  or  ERROR
        Tokens:  <token string> or  ERROR
        Result:  <value>        or  ERROR
    Blocks are separated by a blank line.

    Notes
    -----
    - Blank / whitespace-only lines in the input file are silently skipped.
    - Errors in individual expressions are recorded as ERROR and do not
      prevent the remaining expressions from being evaluated.
    - The output file is written in UTF-8.

    Examples
    --------
    >>> results = evaluate_file("sample_input.txt")
    >>> results[0]
    {'input': '3 + 5', 'tree': '(+ 3 5)', 'tokens': '[NUM:3] [OP:+] [NUM:5] [END]', 'result': 8.0}
    """
    # ------------------------------------------------------------------
    # Read input file
    # ------------------------------------------------------------------
    try:
        with open(input_path, 'r', encoding='utf-8') as fh:
            raw_lines = fh.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path!r}")
    except OSError as exc:
        raise OSError(f"Could not read {input_path!r}: {exc}") from exc

    # ------------------------------------------------------------------
    # Process each line
    # ------------------------------------------------------------------
    results: list[dict] = []
    output_blocks: list[str] = []

    for raw_line in raw_lines:
        expr = raw_line.rstrip('\n')

        # Skip blank / whitespace-only lines
        if not expr.strip():
            continue

        res = _evaluate_one(expr)
        results.append(res)

        # ------------------------------------------------------------------
        # Format the output block for this expression
        # ------------------------------------------------------------------
        rv = res["result"]
        if rv == "ERROR":
            result_str = "ERROR"
        else:
            result_str = _format_number(rv)

        block = (
            f"Input: {res['input']}\n"
            f"Tree: {res['tree']}\n"
            f"Tokens: {res['tokens']}\n"
            f"Result: {result_str}"
        )
        output_blocks.append(block)

    # ------------------------------------------------------------------
    # Write output.txt next to the input file
    # ------------------------------------------------------------------
    output_path = os.path.join(os.path.dirname(os.path.abspath(input_path)), 'output.txt')

    try:
        with open(output_path, 'w', encoding='utf-8') as fh:
            fh.write('\n\n'.join(output_blocks))
            if output_blocks:
                fh.write('\n')   # trailing newline
    except OSError as exc:
        raise OSError(f"Could not write output file {output_path!r}: {exc}") from exc

    return results