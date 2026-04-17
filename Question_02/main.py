"""
main.py
=======
Rakebun owns this file.
 
Responsibility: Command-line interface entry point.
 
Usage
-----
    python main.py <input_file>
    python main.py sample_input.txt
 
The script calls evaluate_file() from evaluator.py and prints a
human-readable summary to stdout.  The actual output.txt is written
by evaluate_file() itself.
"""

import sys
from evaluator import evaluate_file


def _print_summary(results: list[dict]) -> None:
    """
    Print a concise summary of all evaluated expressions to stdout.

    Shows each expression, its result (or ERROR), and a final count of
    successes vs failures.

    Parameters
    ----------
    results : list of dict
        Return value of evaluate_file().
    """
    successes = 0
    errors    = 0

    print()   # blank line for readability
    for i, res in enumerate(results, start=1):
        status = res["result"]
        if status == "ERROR":
            errors += 1
            print(f"  [{i:>3}]  {res['input']!r:40s}  →  ERROR")
        else:
            successes += 1
            # Re-format using the same rule as evaluator.py
            v = status
            display = str(int(v)) if v == int(v) else str(round(v, 4))
            print(f"  [{i:>3}]  {res['input']!r:40s}  →  {display}")

    print()
    print(f"  Done: {successes} OK, {errors} ERROR(s) out of {len(results)} expression(s).")
    print()


def main(argv: list[str] | None = None) -> int:
    """
    Entry point.

    Parameters
    ----------
    argv : list of str, optional
        Command-line arguments (defaults to sys.argv[1:]).

    Returns
    -------
    int
        Exit code: 0 on success, 1 on error.
    """
    args = argv if argv is not None else sys.argv[1:]

    # ------------------------------------------------------------------
    # Validate arguments
    # ------------------------------------------------------------------
    if len(args) != 1:
        print("Usage: python main.py <input_file>", file=sys.stderr)
        print("  e.g. python main.py sample_input.txt", file=sys.stderr)
        return 1

    input_path = args[0]

    # ------------------------------------------------------------------
    # Run the evaluator
    # ------------------------------------------------------------------
    print(f"Reading expressions from: {input_path!r}")

    try:
        results = evaluate_file(input_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"I/O Error: {exc}", file=sys.stderr)
        return 1

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    _print_summary(results)
    print("output.txt has been written to the same directory as the input file.")
    return 0


if __name__ == '__main__':
    sys.exit(main())