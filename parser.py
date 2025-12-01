# parser.py
from tokens import TokenType, Token


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ===== helpers básicos =====

    def current(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def peek_next(self):
        if self.pos + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + 1]

    def check(self, *types):
        if self.pos >= len(self.tokens):
            return False
        return self.current().type in types

    def match(self, *types):
        if self.check(*types):
            self.pos += 1
            return True
        return False

    def consume(self, type_, msg):
        if self.check(type_):
            tok = self.current()
            self.pos += 1
            return tok
        tok = self.current()
        raise ParserError(
            f"[L{tok.line},C{tok.column}] {msg}. Found {tok.type} ({tok.lexeme!r})"
        )

    # ===== entrada principal =====

    def parse(self):
        self.consume(TokenType.BOF, "Expected BOF at start of file")
        self.programa()
        self.consume(TokenType.EOF, "Expected EOF at end of file")

    # ===== gramática alta =====

    # S → BOF Programa EOF
    def programa(self):
        # Programa → ListaDecl
        self.lista_decl()

    # ListaDecl → Decl ListaDecl | ε
    def lista_decl(self):
        while self.es_inicio_decl():
            self.decl()

    def es_inicio_decl(self):
        return self.check(
            TokenType.CLASS,
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.CHAR, TokenType.BOOL, TokenType.VOID
        )

    # Decl → DeclVar | DeclFunc | DeclClase
    def decl(self):
        if self.check(TokenType.CLASS):
            self.decl_clase()
        else:
            self.tipo()
            id_tok = self.consume(TokenType.ID, "Expected identifier after type")
            if self.check(TokenType.PAREN_IZQ):
                self.decl_func_resto(id_tok)
            else:
                self.decl_var_resto(id_tok)

    # ===== declaraciones de variables =====

    # DeclVar → Tipo ListaId PUNTO_COMA
    # (Tipo e ID ya consumidos)
    def decl_var_resto(self, first_id):
        self.inicializacion()
        while self.match(TokenType.COMA):
            self.consume(TokenType.ID, "Expected identifier after ','")
            self.inicializacion()
        self.consume(TokenType.PUNTO_COMA, "Expected ';' after variable declaration")

    # Inicializacion → OP_ASIG Expr | ε
    def inicializacion(self):
        if self.match(TokenType.OP_ASIG):
            self.expr()

    # Tipo → INT | FLOAT | DOUBLE | CHAR | BOOL | VOID
    def tipo(self):
        if not self.match(
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.CHAR, TokenType.BOOL, TokenType.VOID
        ):
            raise ParserError(
                "Expected type (int, float, double, char, bool, void)"
            )

    # ===== funciones =====

    # DeclFunc → Tipo ID PAREN_IZQ Parametros PAREN_DER Bloque
    #          | Tipo ID PAREN_IZQ PAREN_DER Bloque
    def decl_func_resto(self, id_tok):
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after function name")
        if not self.check(TokenType.PAREN_DER):
            self.parametros()
        self.consume(TokenType.PAREN_DER, "Expected ')' after parameters")
        self.bloque()

    # Parametros → ParamLista | ε
    def parametros(self):
        self.param_lista()

    # ParamLista → Param | Param COMA ParamLista
    def param_lista(self):
        self.param()
        while self.match(TokenType.COMA):
            self.param()

    # Param → Tipo ID
    def param(self):
        self.tipo()
        self.consume(TokenType.ID, "Expected parameter name")

    # ===== clases =====

    # DeclClase → CLASS ID LLAVE_IZQ ListaMiembros LLAVE_DER
    def decl_clase(self):
        self.consume(TokenType.CLASS, "Expected 'class'")
        self.consume(TokenType.ID, "Expected class name")
        self.consume(TokenType.LLAVE_IZQ, "Expected '{' after class name")
        self.lista_miembros()
        self.consume(TokenType.LLAVE_DER, "Expected '}' after class body")

    # ListaMiembros → Miembro ListaMiembros | ε
    def lista_miembros(self):
        while self.es_inicio_miembro():
            self.miembro()

    def es_inicio_miembro(self):
        return self.check(
            TokenType.PUBLIC, TokenType.PRIVATE,
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.CHAR, TokenType.BOOL, TokenType.VOID
        )

    # Miembro → ModificadorAcceso DeclVar | ModificadorAcceso DeclFunc
    def miembro(self):
        self.modificador_acceso()
        self.tipo()
        id_tok = self.consume(TokenType.ID, "Expected identifier in class member")
        if self.check(TokenType.PAREN_IZQ):
            self.decl_func_resto(id_tok)
        else:
            self.decl_var_resto(id_tok)

    # ModificadorAcceso → PUBLIC | PRIVATE | ε
    def modificador_acceso(self):
        self.match(TokenType.PUBLIC, TokenType.PRIVATE)

    # ===== bloques y sentencias =====

    # Bloque → LLAVE_IZQ ListaSentencias LLAVE_DER
    def bloque(self):
        self.consume(TokenType.LLAVE_IZQ, "Expected '{'")
        self.lista_sentencias()
        self.consume(TokenType.LLAVE_DER, "Expected '}'")

    # ListaSentencias → Sentencia ListaSentencias | ε
    def lista_sentencias(self):
        while self.es_inicio_sentencia():
            self.sentencia()

    def es_inicio_sentencia(self):
        return (
            self.check(
                TokenType.LLAVE_IZQ, TokenType.IF, TokenType.WHILE,
                TokenType.FOR, TokenType.SWITCH, TokenType.RETURN,
                TokenType.PUNTO_COMA, TokenType.ID
            ) or self.es_inicio_expr()
        )

    def sentencia(self):
        if self.check(TokenType.LLAVE_IZQ):
            self.bloque()
        elif self.check(TokenType.IF):
            self.sentencia_sel()
        elif self.check(TokenType.RETURN):
            self.sentencia_ret()
        else:
            # SentenciaExpr → Expr PUNTO_COMA | PUNTO_COMA
            if self.match(TokenType.PUNTO_COMA):
                return
            self.expr()
            self.consume(TokenType.PUNTO_COMA, "Expected ';' after expression")

    # if / else
    def sentencia_sel(self):
        self.consume(TokenType.IF, "Expected 'if'")
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after 'if'")
        self.expr()
        self.consume(TokenType.PAREN_DER, "Expected ')' after if condition")
        self.sentencia()
        if self.match(TokenType.ELSE):
            self.sentencia()

    # return
    # SentenciaRet → RETURN Expr PUNTO_COMA | RETURN PUNTO_COMA
    def sentencia_ret(self):
        self.consume(TokenType.RETURN, "Expected 'return'")
        if not self.check(TokenType.PUNTO_COMA):
            self.expr()
        self.consume(TokenType.PUNTO_COMA, "Expected ';' after 'return'")

    # ===== expresiones =====

    def expr(self):
        self.expr_asign()

    # ExprAsign → ID OP_ASIG ExprAsign | ExprLogica
    def expr_asign(self):
        if self.check(TokenType.ID) and self.peek_next().type == TokenType.OP_ASIG:
            self.consume(TokenType.ID, "Expected identifier in assignment")
            self.consume(TokenType.OP_ASIG, "Expected '=' in assignment")
            self.expr_asign()
        else:
            self.expr_logica()

    # ExprLogica → ExprAnd (OP_OR ExprAnd)*
    def expr_logica(self):
        self.expr_and()
        while self.match(TokenType.OP_OR):
            self.expr_and()

    # ExprAnd → ExprIgual (OP_AND ExprIgual)*
    def expr_and(self):
        self.expr_igual()
        while self.match(TokenType.OP_AND):
            self.expr_igual()

    # ExprIgual → ExprRel ( (OP_IGUAL | OP_DISTINTO) ExprRel )*
    def expr_igual(self):
        self.expr_rel()
        while self.match(TokenType.OP_IGUAL, TokenType.OP_DISTINTO):
            self.expr_rel()

    # ExprRel → ExprAditiva (relop ExprAditiva)*
    def expr_rel(self):
        self.expr_aditiva()
        while self.match(
            TokenType.OP_MENOR, TokenType.OP_MENOR_IG,
            TokenType.OP_MAYOR, TokenType.OP_MAYOR_IG
        ):
            self.expr_aditiva()

    # ExprAditiva → Term ( (OP_SUMA | OP_RESTA) Term )*
    def expr_aditiva(self):
        self.term()
        while self.match(TokenType.OP_SUMA, TokenType.OP_RESTA):
            self.term()

    # Term → Factor ( (OP_MULT | OP_DIV | OP_MOD) Factor )*
    def term(self):
        self.factor()
        while self.match(TokenType.OP_MULT, TokenType.OP_DIV, TokenType.OP_MOD):
            self.factor()

    # Factor → OP_NOT Factor | Primaria
    def factor(self):
        if self.match(TokenType.OP_NOT):
            self.factor()
        else:
            self.primaria()

    # Primaria → literales | ID | '(' Expr ')'
    def primaria(self):
        if self.match(
            TokenType.NUM_INT, TokenType.NUM_FLOAT,
            TokenType.STRING, TokenType.CHAR_LITERAL,
            TokenType.TRUE, TokenType.FALSE
        ):
            return
        if self.match(TokenType.ID):
            return
        if self.match(TokenType.PAREN_IZQ):
            self.expr()
            self.consume(TokenType.PAREN_DER, "Expected ')' after expression")
            return
        tok = self.current()
        raise ParserError(
            f"[L{tok.line},C{tok.column}] Invalid expression start: "
            f"{tok.type} ({tok.lexeme!r})"
        )

    def es_inicio_expr(self):
        return self.check(
            TokenType.NUM_INT, TokenType.NUM_FLOAT,
            TokenType.STRING, TokenType.CHAR_LITERAL,
            TokenType.TRUE, TokenType.FALSE,
            TokenType.ID, TokenType.PAREN_IZQ
        )
