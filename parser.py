import sys
from lexer import Lexer, TokenType


LABEL_MAP = {
    TokenType.IDENTIFIER: "ID",
    TokenType.INT_LITERAL: "INT_LIT",
    TokenType.FLOAT_LITERAL: "FLOAT_LIT",
    TokenType.PLUS: "PLUS",
    TokenType.MINUS: "MINUS",
    TokenType.STAR: "MUL",
    TokenType.SLASH: "DIV",
    TokenType.PERCENT: "MOD",
    TokenType.ASSIGN: "ASSIGN",
    TokenType.EQ: "EQ",
    TokenType.NEQ: "NEQ",
    TokenType.LT: "LT",
    TokenType.GT: "GT",
    TokenType.LEQ: "LEQ",
    TokenType.GEQ: "GEQ",
    TokenType.AND: "AND",
    TokenType.OR: "OR",
    TokenType.NOT: "NOT",
    TokenType.LPAREN: "LPAREN",
    TokenType.RPAREN: "RPAREN",
    TokenType.LBRACE: "LBRACE",
    TokenType.RBRACE: "RBRACE",
    TokenType.SEMICOLON: "SEMI",
}


class Node:
    def __init__(self, name, children=None, token=None):
        self.name = name
        self.children = children or []
        self.token = token

    def add(self, child):
        self.children.append(child)


def tok_label(token):
    if token.type == TokenType.KEYWORD:
        return f"{token.lexeme.upper()}({token.lexeme})"
    name = LABEL_MAP.get(token.type, token.type.name)
    return f"{name}({token.lexeme})"


def leaf(token):
    return Node(tok_label(token), token=token)


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def cur(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def expect(self, tok_type, lexeme=None):
        tok = self.cur()
        if tok.type != tok_type:
            raise ParseError(
                f"Expected {tok_type.name} but found {tok.type.name} "
                f"'{tok.lexeme}' at line {tok.line}, col {tok.column}"
            )
        if lexeme and tok.lexeme != lexeme:
            raise ParseError(
                f"Expected '{lexeme}' but found '{tok.lexeme}' "
                f"at line {tok.line}, col {tok.column}"
            )
        return self.advance()

    def is_keyword(self, kw):
        return self.cur().type == TokenType.KEYWORD and self.cur().lexeme == kw

    def save(self):
        return self.pos

    def restore(self, pos):
        self.pos = pos

    def parse(self):
        tree = self.program()
        if self.cur().type != TokenType.EOF:
            tok = self.cur()
            raise ParseError(
                f"Unexpected token '{tok.lexeme}' at line {tok.line}, col {tok.column}"
            )
        return tree

    def program(self):
        node = Node("program")
        node.add(self.stmt_list())
        return node

    def stmt_list(self):
        node = Node("stmt_list")
        while self.is_stmt_start():
            node.add(self.stmt())
        return node

    def is_stmt_start(self):
        tok = self.cur()
        if tok.type == TokenType.KEYWORD and tok.lexeme in ("int", "float", "if", "while", "print"):
            return True
        if tok.type == TokenType.IDENTIFIER:
            return True
        if tok.type == TokenType.LBRACE:
            return True
        return False

    def stmt(self):
        tok = self.cur()
        if tok.type == TokenType.KEYWORD and tok.lexeme in ("int", "float"):
            return self.declaration()
        if tok.type == TokenType.IDENTIFIER:
            return self.assignment()
        if self.is_keyword("if"):
            return self.if_stmt()
        if self.is_keyword("while"):
            return self.while_stmt()
        if self.is_keyword("print"):
            return self.print_stmt()
        if tok.type == TokenType.LBRACE:
            return self.block()
        raise ParseError(
            f"Expected statement but found '{tok.lexeme}' "
            f"at line {tok.line}, col {tok.column}"
        )

    def declaration(self):
        node = Node("decl_stmt")
        node.add(leaf(self.advance()))
        node.add(leaf(self.expect(TokenType.IDENTIFIER)))
        node.add(leaf(self.expect(TokenType.SEMICOLON)))
        return node

    def assignment(self):
        node = Node("assign_stmt")
        node.add(leaf(self.expect(TokenType.IDENTIFIER)))
        node.add(leaf(self.expect(TokenType.ASSIGN)))
        node.add(self.expr())
        node.add(leaf(self.expect(TokenType.SEMICOLON)))
        return node

    def if_stmt(self):
        node = Node("if_stmt")
        node.add(leaf(self.expect(TokenType.KEYWORD, "if")))
        node.add(leaf(self.expect(TokenType.LPAREN)))
        node.add(self.bool_expr())
        node.add(leaf(self.expect(TokenType.RPAREN)))
        node.add(self.block())
        if self.is_keyword("else"):
            node.add(leaf(self.advance()))
            node.add(self.block())
        return node

    def while_stmt(self):
        node = Node("while_stmt")
        node.add(leaf(self.expect(TokenType.KEYWORD, "while")))
        node.add(leaf(self.expect(TokenType.LPAREN)))
        node.add(self.bool_expr())
        node.add(leaf(self.expect(TokenType.RPAREN)))
        node.add(self.block())
        return node

    def print_stmt(self):
        node = Node("print_stmt")
        node.add(leaf(self.expect(TokenType.KEYWORD, "print")))
        node.add(leaf(self.expect(TokenType.LPAREN)))
        node.add(self.expr())
        node.add(leaf(self.expect(TokenType.RPAREN)))
        node.add(leaf(self.expect(TokenType.SEMICOLON)))
        return node

    def block(self):
        node = Node("block")
        node.add(leaf(self.expect(TokenType.LBRACE)))
        node.add(self.stmt_list())
        node.add(leaf(self.expect(TokenType.RBRACE)))
        return node

    def bool_expr(self):
        parts = [self.bool_term()]
        while self.cur().type == TokenType.OR:
            parts.append(leaf(self.advance()))
            parts.append(self.bool_term())
        if len(parts) == 1:
            return parts[0]
        node = Node("bool_expr")
        for p in parts:
            node.add(p)
        return node

    def bool_term(self):
        parts = [self.bool_factor()]
        while self.cur().type == TokenType.AND:
            parts.append(leaf(self.advance()))
            parts.append(self.bool_factor())
        if len(parts) == 1:
            return parts[0]
        node = Node("bool_term")
        for p in parts:
            node.add(p)
        return node

    def bool_factor(self):
        tok = self.cur()
        if tok.type == TokenType.NOT:
            node = Node("bool_factor")
            node.add(leaf(self.advance()))
            node.add(self.bool_factor())
            return node
        if tok.type == TokenType.LPAREN:
            saved = self.save()
            try:
                lp = self.expect(TokenType.LPAREN)
                inner = self.bool_expr()
                rp = self.expect(TokenType.RPAREN)
                node = Node("bool_factor")
                node.add(leaf(lp))
                node.add(inner)
                node.add(leaf(rp))
                return node
            except ParseError:
                self.restore(saved)
        return self.comparison()

    def comparison(self):
        node = Node("comparison")
        node.add(self.expr())
        tok = self.cur()
        relops = {TokenType.EQ, TokenType.NEQ, TokenType.LT,
                  TokenType.GT, TokenType.LEQ, TokenType.GEQ}
        if tok.type in relops:
            node.add(leaf(self.advance()))
            node.add(self.expr())
            return node
        raise ParseError(
            f"Expected relational operator but found '{tok.lexeme}' "
            f"at line {tok.line}, col {tok.column}"
        )

    def expr(self):
        parts = [self.term()]
        while self.cur().type in (TokenType.PLUS, TokenType.MINUS):
            parts.append(leaf(self.advance()))
            parts.append(self.term())
        if len(parts) == 1:
            return parts[0]
        node = Node("expr")
        for p in parts:
            node.add(p)
        return node

    def term(self):
        parts = [self.factor()]
        while self.cur().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            parts.append(leaf(self.advance()))
            parts.append(self.factor())
        if len(parts) == 1:
            return parts[0]
        node = Node("term")
        for p in parts:
            node.add(p)
        return node

    def factor(self):
        tok = self.cur()
        node = Node("factor")
        if tok.type == TokenType.LPAREN:
            node.add(leaf(self.advance()))
            node.add(self.expr())
            node.add(leaf(self.expect(TokenType.RPAREN)))
        elif tok.type in (TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL, TokenType.IDENTIFIER):
            node.add(leaf(self.advance()))
        elif tok.type == TokenType.MINUS:
            node.add(leaf(self.advance()))
            node.add(self.factor())
        else:
            raise ParseError(
                f"Expected factor but found '{tok.lexeme}' "
                f"at line {tok.line}, col {tok.column}"
            )
        return node


def print_tree(node, indent=0):
    print("    " * indent + node.name)
    for child in node.children:
        print_tree(child, indent + 1)


def print_cfg():
    print("""
  Production Rules:
  -----------------------------------------------------------------
  Program Structure
   1. program      -> stmt_list
   2. stmt_list    -> stmt stmt_list | (empty)

  Statements
   3. stmt         -> decl_stmt | assign_stmt | if_stmt
                    | while_stmt | print_stmt | block

  Declarations
   4. decl_stmt    -> type ID SEMI
   5. type         -> "int" | "float"

  Assignment
   6. assign_stmt  -> ID ASSIGN expr SEMI

  Control Flow
   7. if_stmt      -> "if" LPAREN bool_expr RPAREN block
                    | "if" LPAREN bool_expr RPAREN block "else" block
   8. while_stmt   -> "while" LPAREN bool_expr RPAREN block

  I/O
   9. print_stmt   -> "print" LPAREN expr RPAREN SEMI

  Block
  10. block        -> LBRACE stmt_list RBRACE

  Boolean Expressions
  11. bool_expr    -> bool_term ( OR bool_term )*
  12. bool_term    -> bool_factor ( AND bool_factor )*
  13. bool_factor  -> NOT bool_factor
                    | LPAREN bool_expr RPAREN
                    | comparison

  Comparisons
  14. comparison   -> expr relop expr
  15. relop        -> EQ | NEQ | LT | GT | LEQ | GEQ

  Arithmetic Expressions
  16. expr         -> term ( (PLUS | MINUS) term )*
  17. term         -> factor ( (MUL | DIV | MOD) factor )*
  18. factor       -> LPAREN expr RPAREN
                    | INT_LIT | FLOAT_LIT | ID
                    | MINUS factor
""")


def get_sentence(node):
    if node.token is not None:
        return [node.token.lexeme]
    parts = []
    for child in node.children:
        parts.extend(get_sentence(child))
    return parts


def first_token(node):
    if node.token is not None:
        return node.token
    for child in node.children:
        tok = first_token(child)
        if tok is not None:
            return tok
    return None


def render_form(items):
    parts = []
    for item in items:
        if item.token is not None:
            parts.append(item.token.lexeme)
        else:
            parts.append(item.name)
    return " ".join(parts)


def derive_leftmost(root):
    form = [root]
    steps = [render_form(form)]
    while True:
        idx = None
        for i, item in enumerate(form):
            if item.token is None:
                idx = i
                break
        if idx is None:
            break
        node = form[idx]
        form = form[:idx] + node.children + form[idx + 1:]
        steps.append(render_form(form))
    return steps


def derive_rightmost(root):
    form = [root]
    steps = [render_form(form)]
    while True:
        idx = None
        for i in range(len(form) - 1, -1, -1):
            if form[i].token is None:
                idx = i
                break
        if idx is None:
            break
        node = form[idx]
        form = form[:idx] + node.children + form[idx + 1:]
        steps.append(render_form(form))
    return steps


def find_first(node, name):
    if node.name == name:
        return node
    for child in node.children:
        result = find_first(child, name)
        if result:
            return result
    return None


def show_derivations(stmt):
    sentence = " ".join(get_sentence(stmt))
    sep = "=" * 70

    print(sep)
    print("SELECTED STATEMENT FOR DERIVATIONS:")
    print(f"    {sentence}")
    print(sep)

    left_steps = derive_leftmost(stmt)
    print("\nLEFTMOST DERIVATION")
    print("-" * 70)
    for i, step in enumerate(left_steps, 1):
        if i == 1:
            print(f"Step {i:2d}       {step}")
        else:
            print(f"Step {i:2d}  =>   {step}")

    right_steps = derive_rightmost(stmt)
    print("\nRIGHTMOST DERIVATION")
    print("-" * 70)
    for i, step in enumerate(right_steps, 1):
        if i == 1:
            print(f"Step {i:2d}       {step}")
        else:
            print(f"Step {i:2d}  =>   {step}")

    print("\nPARSE TREE (selected statement)")
    print("-" * 70)
    print_tree(stmt)


def collect_statements(node, results=None):
    if results is None:
        results = []

    stmt_types = {
        "assign_stmt",
        "decl_stmt",
        "if_stmt",
        "while_stmt",
        "print_stmt"
    }

    if node.name in stmt_types:
        results.append(node)

    for child in node.children:
        collect_statements(child, results)

    return results


def select_statements(statement_infos, choice):
    text = choice.strip().lower()
    if not text:
        return [statement_infos[0]]

    if text in ("all", "*"):
        return statement_infos

    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        return None

    selected = []
    seen_indexes = set()

    for part in parts:
        if not part.isdigit():
            return None

        value = int(part)
        by_line = [info for info in statement_infos if info["line"] == value]

        if by_line:
            for info in by_line:
                if info["index"] not in seen_indexes:
                    selected.append(info)
                    seen_indexes.add(info["index"])
            continue

        if 1 <= value <= len(statement_infos):
            info = statement_infos[value - 1]
            if info["index"] not in seen_indexes:
                selected.append(info)
                seen_indexes.add(info["index"])
            continue

        return None

    return selected

def main():
    if len(sys.argv) < 2:
        print("Usage: python parser.py <source_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file '{filepath}' not found.")
        sys.exit(1)

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    sep = "=" * 70

    print("CONTEXT-FREE GRAMMAR (CFG)")
    print(sep)
    print_cfg()

    print(sep)
    print("PHASE 2: SYNTACTIC ANALYSIS (PARSING)")
    print(sep)

    parser = Parser(tokens)
    try:
        tree = parser.parse()
        print("[OK] Syntax OK")
    except ParseError as e:
        print(f"[ERROR] Syntax Error: {e}")
        sys.exit(1)

    print(f"\n{sep}")
    print("PARSE TREE (full program)")
    print(sep)
    print_tree(tree)

    print(f"\n{sep}")
    print("\n" + "=" * 70)
    print("STATEMENTS DETECTED IN PROGRAM")
    print("=" * 70)

    statements = collect_statements(tree)

    if not statements:
        print("No derivable statements found.")
        return

    statement_infos = []
    for i, stmt in enumerate(statements, 1):
        sentence = " ".join(get_sentence(stmt))
        tok = first_token(stmt)
        line = tok.line if tok is not None else -1
        statement_infos.append({
            "index": i,
            "line": line,
            "sentence": sentence,
            "node": stmt,
        })
        if line >= 0:
            print(f"{i:2d}. [line {line}] {sentence}")
        else:
            print(f"{i:2d}. [line ?] {sentence}")

    print("\nEnter statement number, source line number, comma list, or 'all':")
    try:
        choice = input("> ").strip()
    except EOFError:
        choice = "all"
        print("No input detected; showing derivations for all statements.")

    selected = select_statements(statement_infos, choice)
    if not selected:
        print("Invalid selection. Use statement number(s), line number(s), or 'all'.")
        return

    for info in selected:
        print("\n" + sep)
        print(f"STATEMENT #{info['index']} (line {info['line']})")
        print(sep)
        show_derivations(info["node"])


if __name__ == "__main__":
    main()
