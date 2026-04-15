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