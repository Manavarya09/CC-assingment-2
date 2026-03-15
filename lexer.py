import re 
import sys 
from enum import Enum, auto 
from dataclasses import dataclass 

 
class TokenType(Enum): 
    KEYWORD         = auto() 
    IDENTIFIER      = auto() 
    INT_LITERAL     = auto() 
    FLOAT_LITERAL   = auto() 
    PLUS            = auto() 
    MINUS           = auto() 
    STAR            = auto() 
    SLASH           = auto() 
    PERCENT         = auto() 
    ASSIGN          = auto() 
    EQ              = auto() 
    NEQ             = auto() 
    LT              = auto() 
    GT              = auto() 
    LEQ             = auto() 
    GEQ             = auto() 
    AND             = auto() 
    OR              = auto() 
    NOT             = auto() 
    LPAREN          = auto() 
    RPAREN          = auto() 
    LBRACE          = auto() 
    RBRACE          = auto() 
    SEMICOLON       = auto() 
    COMMA           = auto() 
    EOF             = auto() 
 
KEYWORDS = {"int", "float", "if", "else", "while", "print"} 
 
TOKEN_SPECIFICATION = [ 
    ("MULTI_COMMENT",  r'/\*[\s\S]*?\*/'), 
    ("SINGLE_COMMENT", r'//[^\n]*'), 
    ("WHITESPACE",     r'[ \t\r\n]+'), 
    ("FLOAT_LITERAL",  r'\d+\.\d*|\d*\.\d+'), 
    ("INT_LITERAL",    r'\d+'), 
    ("EQ",             r'=='), 
    ("NEQ",            r'!='), 
    ("LEQ",            r'<='), 
    ("GEQ",            r'>='), 
    ("AND",            r'&&'), 
    ("OR",             r'\|\|'), 
    ("ASSIGN",         r'='), 
    ("NOT",            r'!'), 
    ("LT",             r'<'), 
    ("GT",             r'>'), 
    ("PLUS",           r'\+'), 
    ("MINUS",          r'-'), 
    ("STAR",           r'\*'), 
    ("SLASH",          r'/'), 
    ("PERCENT",        r'%'), 
    ("LPAREN",         r'\('), 
    ("RPAREN",         r'\)'), 
    ("LBRACE",         r'\{'), 
    ("RBRACE",         r'\}'), 
    ("SEMICOLON",      r';'), 
    ("COMMA",          r','), 
    ("WORD",           r'[a-zA-Z_][a-zA-Z0-9_]*'), 
    ("ILLEGAL",        r'.'), 
] 
 
MASTER_PATTERN = '|'.join( 
    f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION 
) 
MASTER_RE = re.compile(MASTER_PATTERN) 
 
@dataclass 
class Token: 
    type:   TokenType 
    lexeme: str 
    line:   int 
    column: int 
 
    def __repr__(self): 
        return (f"Token({self.type.name:15s}, {self.lexeme!r:15s}, " 
                f"line={self.line}, col={self.column})") 
 
@dataclass 
class LexicalError: 
    char:   str 
    line:   int 
    column: int 
    message: str 
 
    def __repr__(self): 
        return (f"LexicalError(line={self.line}, col={self.column}, " 
                f"char={self.char!r}, msg={self.message!r})") 
 
class Lexer: 
    def __init__(self, source): 
        self.source = source 
        self.tokens = [] 
        self.errors = [] 
 
    def _line_col(self, offset): 
        line = self.source.count('\n', 0, offset) + 1 
        last_nl = self.source.rfind('\n', 0, offset) 
        col = offset - last_nl 
        return line, col 
 
    def tokenize(self): 
        for mo in MASTER_RE.finditer(self.source): 
            kind = mo.lastgroup 
            lexeme = mo.group() 
            line, col = self._line_col(mo.start()) 
 
            if kind in ("WHITESPACE", "SINGLE_COMMENT", "MULTI_COMMENT"): 
                continue 
 
            if kind == "ILLEGAL": 
                err = LexicalError( 
                    char=lexeme, line=line, column=col, 
                    message=f"Unexpected character '{lexeme}'" 
                ) 
                self.errors.append(err) 
                continue 
 
            if kind == "WORD": 
                if lexeme in KEYWORDS: 
                    tok_type = TokenType.KEYWORD 
                else: 
                    tok_type = TokenType.IDENTIFIER 
            else: 
                tok_type = TokenType[kind] 
 
            self.tokens.append(Token(tok_type, lexeme, line, col)) 
 
        eof_line, eof_col = self._line_col(len(self.source)) 
        self.tokens.append(Token(TokenType.EOF, "<EOF>", eof_line, eof_col)) 
        return self.tokens 
 
def print_token_table(tokens): 
    print("\n  TOKEN STREAM") 
    print(f"  {'#':>4}  {'Token Type':<17} {'Lexeme':<17} {'Line':>5}  {'Col':>4}") 
    print() 
    for i, tok in enumerate(tokens, 1): 
        print(f"  {i:4d}  {tok.type.name:<17} {tok.lexeme:<17} {tok.line:5d}  {tok.column:4d}") 
    print(f"\n  Total tokens (including EOF): {len(tokens)}") 
 
def print_error_report(errors): 
    if not errors: 
        print("\n  LEXICAL ERROR REPORT") 
        print("  No lexical errors detected. All characters were successfully tokenized.") 
    else: 
        print("\n  LEXICAL ERRORS") 
        print(f"  {'#':>4}  {'Char':<8} {'Line':>5}  {'Col':>4}  {'Message'}") 
        print() 
        for i, err in enumerate(errors, 1): 
            print(f"  {i:4d}  {err.char!r:<8} {err.line:5d}  {err.column:4d}  {err.message}") 
 

 
def main(): 
    if len(sys.argv) < 2: 
        print("Usage: python lexer.py <source_file>") 
        sys.exit(1) 
 
    filepath = sys.argv[1] 
    try: 
        with open(filepath, 'r', encoding='utf-8') as f: 
            source_code = f.read() 
    except FileNotFoundError: 
        print(f"Error: file '{filepath}' not found.") 
        sys.exit(1) 
 
    lexer = Lexer(source_code) 
    tokens = lexer.tokenize() 
 
    print_token_table(tokens) 
    print_error_report(lexer.errors) 
 
if __name__ == "__main__": 
    main()