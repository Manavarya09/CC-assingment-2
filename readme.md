# Mini Compiler — Lexical & Syntactic Front-End

This project implements the lexical analysis and CFG-based syntactic analysis (recursive-descent parser) phases for the course assignment. The repository is designed to consume the token stream produced by the lexer, parse the program according to a context-free grammar, and demonstrate leftmost/rightmost derivations and parse trees as required by Question 2.

## Question 2: What is required

Question 2 asks you to:

- Design a complete Context-Free Grammar (CFG) that generates the core language (declarations, assignments, arithmetic and boolean expressions, if-else, while, blocks, print).
- Ensure the grammar can generate the provided evaluation program without modification.
- Demonstrate syntactic validation by showing a leftmost derivation, a rightmost derivation, and the parse tree for at least one non-trivial statement.
- The parser must consume the token stream produced by the lexical analyzer.

## How this implementation satisfies Q2

- Grammar: The CFG is printed by `parser.py` via the `print_cfg()` function and is the grammar implemented by the parser. It includes productions for `program`, `stmt_list`, `stmt`, `decl_stmt`, `assign_stmt`, `if_stmt`, `while_stmt`, `print_stmt`, `block`, `bool_expr`, `bool_term`, `bool_factor`, `comparison`, `expr`, `term`, and `factor`.
- Lexer → Parser: `main()` in `parser.py` creates a `Lexer(source)`, calls `tokenize()` and then passes the returned token list to `Parser(tokens)` — so the parser directly consumes the lexer’s token stream.
- Derivations & Parse Tree: After successful parsing the program, `parser.py` collects top-level statements and prompts the user to select a statement (or `all`). For each selected statement it prints:
	- leftmost derivation (via `derive_leftmost`),
	- rightmost derivation (via `derive_rightmost`), and
	- the parse tree (via `print_tree`).

These outputs directly demonstrate syntactic validation exactly as required by Question 2.

## Files and key code explanation

- `lexer.py`
	- Implements token definitions using regex and a `Lexer` class.
	- `tokenize()` returns a list of `Token(type, lexeme, line, column)` and appends an `EOF` token.
	- `print_token_table()` shows the token stream (used for Question 1).

- `parser.py`
	- `Node`: lightweight parse-tree node (name, children, optional `token`).
	- `Parser` (recursive-descent): operates over a token list with methods:
		- `program()`, `stmt_list()`, `stmt()` — top-level control
		- `declaration()`, `assignment()`, `if_stmt()`, `while_stmt()`, `print_stmt()`, `block()` — statement-level rules
		- `bool_expr()`, `bool_term()`, `bool_factor()`, `comparison()` — boolean and relational handling
		- `expr()`, `term()`, `factor()` — arithmetic expressions with precedence
	- Error handling: `expect()` raises `ParseError` with line/col for clear diagnostics.
	- Derivation helpers: `derive_leftmost`, `derive_rightmost`, `render_form` build and show derivation steps.
	- `collect_statements()` finds derivable statements for demonstration; `show_derivations()` prints derivations + parse tree.

## How to run (examples you can demo)

1) Print tokens (Question 1):

```bash
python lexer.py evaluation_program.src
```

2) Parse and interactively show derivations (Question 2):

```bash
python parser.py evaluation_program.src
```

When prompted, enter a statement number, a source line number, comma list, or `all`.
To script showing the while statement (example):

```bash
printf '8\n' | python parser.py evaluation_program.src
```

To show derivations for all statements:

```bash
printf 'all\n' | python parser.py evaluation_program.src
```

## What to present for the evaluation (suggestion)

- Show the token stream from `lexer.py` to demonstrate Question 1.
- Use `parser.py` and select a **non-trivial statement** (e.g., the `while` loop or the `if (!(avg < 5.0))` statement) and present:
	- leftmost derivation
	- rightmost derivation
	- the parse tree

These three outputs satisfy the syntactic validation requirements of Question 2.

## Next steps (recommended)

- Add semantic analysis: symbol table with scopes, undeclared/multiple declaration checks, and type checking.
- Generate intermediate code (three-address code) and apply simple optimizations.
- Add a small README section for how to present outputs in the viva.

---

If you want, I can now:

- add a short “presenter’s notes” section to this README with exact terminal commands and sample screenshots of outputs, or
- implement the symbol table and basic semantic checks next.

If you want me to proceed, tell me which next step to take.

hello world