# lexer.py
from tokens import TokenType, Token


class LexError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_tokens(self) -> list[Token]:
        # BOF
        self.tokens.append(Token(TokenType.BOF, "BOF", 1, 1))

        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        # EOF
        self.tokens.append(Token(TokenType.EOF, "EOF", self.line, self.column))
        return self.tokens

    # ----------------- helpers básicos -----------------

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        self.column += 1
        return ch

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def add_token(self, type_: TokenType, lexeme: str = None):
        if lexeme is None:
            lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(type_, lexeme, self.line, self.column - len(lexeme)))

    # ----------------- lógica principal -----------------

    def scan_token(self):
        c = self.advance()

        # espacios
        if c in (" ", "\r", "\t"):
            return
        if c == "\n":
            self.line += 1
            self.column = 1
            return

        # símbolos simples
        if c == "(":
            self.add_token(TokenType.PAREN_IZQ)
        elif c == ")":
            self.add_token(TokenType.PAREN_DER)
        elif c == "{":
            self.add_token(TokenType.LLAVE_IZQ)
        elif c == "}":
            self.add_token(TokenType.LLAVE_DER)
        elif c == "[":
            self.add_token(TokenType.CORCHETE_IZQ)
        elif c == "]":
            self.add_token(TokenType.CORCHETE_DER)
        elif c == ";":
            self.add_token(TokenType.PUNTO_COMA)
        elif c == ",":
            self.add_token(TokenType.COMA)
        elif c == ".":
            self.add_token(TokenType.PUNTO)

        # operadores
        elif c == "+":
            if self.match("+"):
                self.add_token(TokenType.OP_INC)
            else:
                self.add_token(TokenType.OP_SUMA)
        elif c == "-":
            if self.match("-"):
                self.add_token(TokenType.OP_DEC)
            else:
                self.add_token(TokenType.OP_RESTA)
        elif c == "*":
            self.add_token(TokenType.OP_MULT)
        elif c == "%":
            self.add_token(TokenType.OP_MOD)
        elif c == "/":
            if self.match("/"):
                # comentario de línea: ignorar hasta fin de línea
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
                # no agregamos token
            elif self.match("*"):
                # comentario de bloque
                self.block_comment()
            else:
                self.add_token(TokenType.OP_DIV)
        elif c == "=":
            if self.match("="):
                self.add_token(TokenType.OP_IGUAL)
            else:
                self.add_token(TokenType.OP_ASIG)
        elif c == "!":
            if self.match("="):
                self.add_token(TokenType.OP_DISTINTO)
            else:
                self.add_token(TokenType.OP_NOT)
        elif c == "<":
            if self.match("="):
                self.add_token(TokenType.OP_MENOR_IG)
            else:
                self.add_token(TokenType.OP_MENOR)
        elif c == ">":
            if self.match("="):
                self.add_token(TokenType.OP_MAYOR_IG)
            else:
                self.add_token(TokenType.OP_MAYOR)
        elif c == "&":
            if self.match("&"):
                self.add_token(TokenType.OP_AND)
            else:
                raise LexError(f"[L{self.line}] Unexpected '&' (wanted '&&')")
        elif c == "|":
            if self.match("|"):
                self.add_token(TokenType.OP_OR)
            else:
                raise LexError(f"[L{self.line}] Unexpected '|' (wanted '||')")

        # literales
        elif c == '"':
            self.string()
        elif c == "'":
            self.char_literal()
        elif c.isdigit():
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            raise LexError(f"[L{self.line}] Unexpected character: {c!r}")

    # ----------------- comentarios -----------------

    def block_comment(self):
        # ya leímos '/*'
        while not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
                self.column = 1
                self.advance()
                continue
            if self.peek() == "*" and self.peek_next() == "/":
                # consume '*/'
                self.advance()
                self.advance()
                return
            self.advance()
        # si sale del while sin encontrar */, error
        raise LexError(f"[L{self.line}] Unterminated block comment")

    # ----------------- literales -----------------

    def string(self):
        # ya vimos la primera comilla "
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
                self.column = 1
            self.advance()
        if self.is_at_end():
            raise LexError(f"[L{self.line}] Unterminated string literal")
        # consume la comilla de cierre
        self.advance()
        # contenido sin comillas
        value = self.source[self.start + 1:self.current - 1]
        self.tokens.append(Token(TokenType.STRING, value, self.line, self.column - len(value) - 2))

    def char_literal(self):
        # muy simple: 'a'
        if self.is_at_end() or self.peek() == "\n":
            raise LexError(f"[L{self.line}] Unterminated char literal")
        ch = self.advance()
        if self.peek() != "'":
            raise LexError(f"[L{self.line}] Char literal must be one character")
        self.advance()  # cierra '
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(TokenType.CHAR_LITERAL, lexeme, self.line, self.column - len(lexeme)))

    def number(self):
        # parte entera
        while self.peek().isdigit():
            self.advance()
        # parte decimal opcional
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()  # consume '.'
            while self.peek().isdigit():
                self.advance()
            lexeme = self.source[self.start:self.current]
            self.add_token(TokenType.NUM_FLOAT, lexeme)
        else:
            lexeme = self.source[self.start:self.current]
            self.add_token(TokenType.NUM_INT, lexeme)

    # ----------------- identificadores / keywords -----------------

    def is_alpha(self, c: str) -> bool:
        return c.isalpha() or c == "_"

    def is_alnum(self, c: str) -> bool:
        return c.isalnum() or c == "_"

    def identifier(self):
        while self.is_alnum(self.peek()):
            self.advance()
        text = self.source[self.start:self.current]

        keywords = {
            "int": TokenType.INT,
            "float": TokenType.FLOAT,
            "double": TokenType.DOUBLE,
            "char": TokenType.CHAR,
            "bool": TokenType.BOOL,
            "void": TokenType.VOID,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "switch": TokenType.SWITCH,
            "case": TokenType.CASE,
            "default": TokenType.DEFAULT,
            "return": TokenType.RETURN,
            "class": TokenType.CLASS,
            "public": TokenType.PUBLIC,
            "private": TokenType.PRIVATE,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
        }

        type_ = keywords.get(text, TokenType.ID)
        self.add_token(type_, text)
