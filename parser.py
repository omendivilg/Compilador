# parser.py
from tokens import TokenType, Token
from ast_nodes import *


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

    def parse(self) -> Program:
        """Análisis léxico: retorna el AST raíz"""
        self.consume(TokenType.BOF, "Expected BOF at start of file")
        program = self.programa()
        self.consume(TokenType.EOF, "Expected EOF at end of file")
        return program

    # ===== gramática alta =====

    # S → BOF Programa EOF
    def programa(self) -> Program:
        # Programa → ListaDecl
        declarations = self.lista_decl()
        return Program(declarations)

    # ListaDecl → Decl ListaDecl | ε
    def lista_decl(self) -> List[Declaration]:
        declarations = []
        while self.es_inicio_decl():
            decl = self.decl()
            if decl:
                declarations.append(decl)
        return declarations

    def es_inicio_decl(self):
        return self.check(
            TokenType.CLASS,
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.CHAR, TokenType.BOOL, TokenType.VOID
        )

    # Decl → DeclVar | DeclFunc | DeclClase
    def decl(self) -> Optional[Declaration]:
        if self.check(TokenType.CLASS):
            return self.decl_clase()
        else:
            type_token = self.tipo()
            id_tok = self.consume(TokenType.ID, "Expected identifier after type")
            if self.check(TokenType.PAREN_IZQ):
                return self.decl_func_resto(type_token, id_tok)
            else:
                return self.decl_var_resto(type_token, id_tok)

    # ===== declaraciones de variables =====

    # DeclVar → Tipo ListaId PUNTO_COMA
    def decl_var_resto(self, type_token: Token, first_id: Token) -> VarDecl:
        declarators = []
        
        # Primer item
        init_expr = self.inicializacion()
        declarators.append(VarDeclarator(first_id, init_expr, is_array=False))
        
        # Items adicionales
        while self.match(TokenType.COMA):
            id_token = self.consume(TokenType.ID, "Expected identifier after ','")
            init_expr = self.inicializacion()
            declarators.append(VarDeclarator(id_token, init_expr, is_array=False))
        
        self.consume(TokenType.PUNTO_COMA, "Expected ';' after variable declaration")
        return VarDecl(type_token, declarators)

    # DeclVarSinPunto → TIPO LISTAID (sin punto y coma, para for init)
    def decl_var_sin_punto(self, type_token: Token, first_id: Token) -> VarDeclSinPunto:
        declarators = []
        
        # Primer item
        init_expr = self.inicializacion()
        declarators.append(VarDeclarator(first_id, init_expr, is_array=False))
        
        # Items adicionales
        while self.match(TokenType.COMA):
            id_token = self.consume(TokenType.ID, "Expected identifier after ','")
            init_expr = self.inicializacion()
            declarators.append(VarDeclarator(id_token, init_expr, is_array=False))
        
        return VarDeclSinPunto(type_token, declarators)

    # Inicializacion → OP_ASIG Expr | ε
    def inicializacion(self) -> Optional[Expression]:
        if self.match(TokenType.OP_ASIG):
            return self.expr()
        return None

    # Tipo → INT | FLOAT | DOUBLE | CHAR | BOOL | VOID
    def tipo(self) -> Token:
        """Retorna el token del tipo"""
        if self.match(
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.CHAR, TokenType.BOOL, TokenType.VOID
        ):
            return self.tokens[self.pos - 1]  # Devuelve el token que acabamos de consumir
        raise ParserError(
            "Expected type (int, float, double, char, bool, void)"
        )

    # ===== funciones =====

    # DeclFunc → Tipo ID PAREN_IZQ Parametros PAREN_DER Bloque
    def decl_func_resto(self, return_type: Token, id_tok: Token) -> FuncDecl:
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after function name")
        
        parameters = []
        if not self.check(TokenType.PAREN_DER):
            parameters = self.parametros()
        
        self.consume(TokenType.PAREN_DER, "Expected ')' after parameters")
        body = self.bloque()
        
        return FuncDecl(return_type, id_tok, parameters, body)

    # Parametros → ParamLista | ε
    def parametros(self) -> List[Param]:
        return self.param_lista()

    # ParamLista → Param | Param COMA ParamLista
    def param_lista(self) -> List[Param]:
        params = [self.param()]
        while self.match(TokenType.COMA):
            params.append(self.param())
        return params

    # Param → Tipo ID
    def param(self) -> Param:
        type_token = self.tipo()
        name_token = self.consume(TokenType.ID, "Expected parameter name")
        return Param(type_token, name_token)

    # ===== clases =====

    # DeclClase → CLASS ID LLAVE_IZQ ListaMiembros LLAVE_DER
    def decl_clase(self) -> ClassDecl:
        self.consume(TokenType.CLASS, "Expected 'class'")
        class_name = self.consume(TokenType.ID, "Expected class name")
        self.consume(TokenType.LLAVE_IZQ, "Expected '{' after class name")
        
        members = self.lista_miembros()
        
        self.consume(TokenType.LLAVE_DER, "Expected '}' after class body")
        return ClassDecl(class_name, members)

    # ListaMiembros → Miembro ListaMiembros | ε
    def lista_miembros(self) -> List[ClassMember]:
        members = []
        while self.es_inicio_miembro():
            member = self.miembro()
            if member:
                members.append(member)
        return members

    def es_inicio_miembro(self):
        return self.check(
            TokenType.PUBLIC, TokenType.PRIVATE,
            TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
            TokenType.CHAR, TokenType.BOOL, TokenType.VOID
        )

    # Miembro → ModificadorAcceso DeclVar | ModificadorAcceso DeclFunc
    def miembro(self) -> Optional[ClassMember]:
        access_mod = self.modificador_acceso()
        type_token = self.tipo()
        id_tok = self.consume(TokenType.ID, "Expected identifier in class member")
        
        if self.check(TokenType.PAREN_IZQ):
            decl = self.decl_func_resto(type_token, id_tok)
        else:
            decl = self.decl_var_resto(type_token, id_tok)
        
        return ClassMember(access_mod, decl)

    # ModificadorAcceso → PUBLIC | PRIVATE | ε
    def modificador_acceso(self) -> Optional[Token]:
        """Retorna el token del modificador o None"""
        if self.match(TokenType.PUBLIC):
            return self.tokens[self.pos - 1]
        if self.match(TokenType.PRIVATE):
            return self.tokens[self.pos - 1]
        return None

    # ===== bloques y sentencias =====

    # Bloque → LLAVE_IZQ ListaSentencias LLAVE_DER
    def bloque(self) -> BlockStmt:
        self.consume(TokenType.LLAVE_IZQ, "Expected '{'")
        statements = self.lista_sentencias()
        self.consume(TokenType.LLAVE_DER, "Expected '}'")
        return BlockStmt(statements)

    # ListaSentencias → Sentencia ListaSentencias | ε
    def lista_sentencias(self) -> List[Statement]:
        statements = []
        while self.es_inicio_sentencia():
            stmt = self.sentencia()
            if stmt:
                statements.append(stmt)
        return statements

    def es_inicio_sentencia(self):
        return (
            self.check(
                TokenType.LLAVE_IZQ, TokenType.IF, TokenType.WHILE,
                TokenType.FOR, TokenType.SWITCH, TokenType.RETURN,
                TokenType.PUNTO_COMA, TokenType.ID,
                # Añadir tipos para declaraciones de variables
                TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                TokenType.CHAR, TokenType.BOOL, TokenType.VOID
            ) or self.es_inicio_expr()
        )

    def sentencia(self) -> Optional[Statement]:
        # Declaración de variable dentro de sentencia (ej: en bloques)
        if self.check(TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                     TokenType.CHAR, TokenType.BOOL):
            type_token = self.tipo()
            id_tok = self.consume(TokenType.ID, "Expected identifier after type")
            
            declarators = []
            
            # Puede ser un arreglo: int arr[10];
            if self.match(TokenType.CORCHETE_IZQ):
                # Es una declaración de arreglo
                size_expr = self.expr()
                self.consume(TokenType.CORCHETE_DER, "Expected ']' after array size")
                declarators.append(VarDeclarator(id_tok, None, is_array=True))
                
                # Mas items si hay comas
                while self.match(TokenType.COMA):
                    id_token = self.consume(TokenType.ID, "Expected identifier after ','")
                    is_arr = False
                    if self.match(TokenType.CORCHETE_IZQ):
                        self.expr()
                        self.consume(TokenType.CORCHETE_DER, "Expected ']'")
                        is_arr = True
                    declarators.append(VarDeclarator(id_token, None, is_array=is_arr))
                
                self.consume(TokenType.PUNTO_COMA, "Expected ';' after array declaration")
            else:
                # Variable normal
                init_expr = None
                if self.match(TokenType.OP_ASIG):
                    init_expr = self.expr()
                declarators.append(VarDeclarator(id_tok, init_expr, is_array=False))
                
                while self.match(TokenType.COMA):
                    id_token = self.consume(TokenType.ID, "Expected identifier")
                    init_expr = None
                    if self.match(TokenType.OP_ASIG):
                        init_expr = self.expr()
                    declarators.append(VarDeclarator(id_token, init_expr, is_array=False))
                
                self.consume(TokenType.PUNTO_COMA, "Expected ';' after variable declaration")
            
            # Retornar como VarDeclStmt
            var_decl = VarDecl(type_token, declarators)
            return VarDeclStmt(var_decl)
        
        elif self.check(TokenType.LLAVE_IZQ):
            return self.bloque()
        elif self.check(TokenType.IF):
            return self.sentencia_sel()
        elif self.check(TokenType.WHILE):
            return self.sentencia_while()
        elif self.check(TokenType.FOR):
            return self.sentencia_for()
        elif self.check(TokenType.SWITCH):
            return self.sentencia_switch()
        elif self.check(TokenType.RETURN):
            return self.sentencia_ret()
        else:
            # SentenciaExpr → Expr PUNTO_COMA | PUNTO_COMA
            if self.match(TokenType.PUNTO_COMA):
                return ExprStmt(None)
            expr_node = self.expr()
            self.consume(TokenType.PUNTO_COMA, "Expected ';' after expression")
            return ExprStmt(expr_node)

    # if / else
    def sentencia_sel(self) -> IfStmt:
        self.consume(TokenType.IF, "Expected 'if'")
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after 'if'")
        condition = self.expr()
        self.consume(TokenType.PAREN_DER, "Expected ')' after if condition")
        then_stmt = self.sentencia()
        
        else_stmt = None
        if self.match(TokenType.ELSE):
            else_stmt = self.sentencia()
        
        return IfStmt(condition, then_stmt, else_stmt)

    # while
    def sentencia_while(self) -> WhileStmt:
        self.consume(TokenType.WHILE, "Expected 'while'")
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after 'while'")
        condition = self.expr()
        self.consume(TokenType.PAREN_DER, "Expected ')' after while condition")
        body = self.sentencia()
        
        return WhileStmt(condition, body)

    # for
    def sentencia_for(self) -> ForStmt:
        self.consume(TokenType.FOR, "Expected 'for'")
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after 'for'")
        
        # ForInit puede ser: Expr, DeclVar (sin punto y coma), o vacío
        init = None
        if not self.check(TokenType.PUNTO_COMA):
            # Verificar si es una declaración de variable
            if self.check(TokenType.INT, TokenType.FLOAT, TokenType.DOUBLE,
                         TokenType.CHAR, TokenType.BOOL):
                # Es una declaración de variable (sin el PUNTO_COMA final)
                type_token = self.tipo()
                id_tok = self.consume(TokenType.ID, "Expected identifier in for init")
                
                # Inicializador opcional
                init_expr = None
                if self.match(TokenType.OP_ASIG):
                    init_expr = self.expr()
                declarators = [VarDeclarator(id_tok, init_expr, is_array=False)]
                
                # Más items si hay comas
                while self.match(TokenType.COMA):
                    id_token = self.consume(TokenType.ID, "Expected identifier after ','")
                    init_expr = None
                    if self.match(TokenType.OP_ASIG):
                        init_expr = self.expr()
                    declarators.append(VarDeclarator(id_token, init_expr, is_array=False))
                
                init = VarDeclSinPunto(type_token, declarators)
            else:
                # Es una expresión normal
                init = self.expr()
        
        self.consume(TokenType.PUNTO_COMA, "Expected ';' after for init")
        
        condition = None
        if not self.check(TokenType.PUNTO_COMA):
            condition = self.expr()
        self.consume(TokenType.PUNTO_COMA, "Expected ';' after for condition")
        
        update = None
        if not self.check(TokenType.PAREN_DER):
            update = self.expr()
        self.consume(TokenType.PAREN_DER, "Expected ')' after for clauses")
        
        body = self.sentencia()
        
        return ForStmt(init, condition, update, body)

    # switch
    def sentencia_switch(self) -> SwitchStmt:
        self.consume(TokenType.SWITCH, "Expected 'switch'")
        self.consume(TokenType.PAREN_IZQ, "Expected '(' after 'switch'")
        expr_node = self.expr()
        self.consume(TokenType.PAREN_DER, "Expected ')' after switch expr")
        self.consume(TokenType.LLAVE_IZQ, "Expected '{' after switch header")
        
        cases = self.lista_casos()
        
        self.consume(TokenType.LLAVE_DER, "Expected '}' after switch body")
        
        return SwitchStmt(expr_node, cases)

    # ListaCasos → Caso ListaCasos | ε
    def lista_casos(self) -> List[CaseStmt]:
        cases = []
        while self.check(TokenType.CASE, TokenType.DEFAULT):
            case_node = self.caso()
            if case_node:
                cases.append(case_node)
        return cases

    # Caso → case Expr PUNTO_COMA ListaSentencias | default PUNTO_COMA ListaSentencias
    def caso(self) -> Optional[CaseStmt]:
        if self.match(TokenType.CASE):
            case_expr = self.expr()
            self.consume(TokenType.PUNTO_COMA, "Expected ':' after case expression")
            statements = self.lista_sentencias()
            return CaseStmt(case_expr, statements)
        elif self.match(TokenType.DEFAULT):
            self.consume(TokenType.PUNTO_COMA, "Expected ':' after default")
            statements = self.lista_sentencias()
            return CaseStmt(None, statements)
        return None

    # return
    # SentenciaRet → RETURN Expr PUNTO_COMA | RETURN PUNTO_COMA
    def sentencia_ret(self) -> ReturnStmt:
        self.consume(TokenType.RETURN, "Expected 'return'")
        
        return_expr = None
        if not self.check(TokenType.PUNTO_COMA):
            return_expr = self.expr()
        
        self.consume(TokenType.PUNTO_COMA, "Expected ';' after 'return'")
        return ReturnStmt(return_expr)

    # ===== expresiones =====

    def expr(self) -> Expression:
        return self.expr_asign()

    # ExprAsign → ID OP_ASIG ExprAsign | ID[Expr] OP_ASIG ExprAsign | ExprLogica
    def expr_asign(self) -> Expression:
        # Intenta parsear como asignación
        left = self.expr_logica()
        
        # Verifica si es una asignación
        if self.match(TokenType.OP_ASIG):
            # left debe ser IdentifierExpr o IndexExpr
            if isinstance(left, (IdentifierExpr, IndexExpr)):
                value = self.expr_asign()  # Recursivo para asignación derecha
                return AssignExpr(left, value)
            else:
                raise ParserError(
                    f"[L{self.current().line}] Invalid assignment target"
                )
        
        return left

    # ExprLogica → ExprAnd (OP_OR ExprAnd)*
    def expr_logica(self) -> Expression:
        left = self.expr_and()
        while self.check(TokenType.OP_OR):
            op_tok = self.current()
            self.match(TokenType.OP_OR)
            right = self.expr_and()
            left = LogicalOrExpr(left, op_tok, right)
        return left

    # ExprAnd → ExprIgual (OP_AND ExprIgual)*
    def expr_and(self) -> Expression:
        left = self.expr_igual()
        while self.check(TokenType.OP_AND):
            op_tok = self.current()
            self.match(TokenType.OP_AND)
            right = self.expr_igual()
            left = LogicalAndExpr(left, op_tok, right)
        return left

    # ExprIgual → ExprRel ( (OP_IGUAL | OP_DISTINTO) ExprRel )*
    def expr_igual(self) -> Expression:
        left = self.expr_rel()
        while self.check(TokenType.OP_IGUAL, TokenType.OP_DISTINTO):
            op_tok = self.current()
            self.match(TokenType.OP_IGUAL, TokenType.OP_DISTINTO)
            right = self.expr_rel()
            left = EqualityExpr(left, op_tok, right)
        return left

    # ExprRel → ExprAditiva (relop ExprAditiva)*
    def expr_rel(self) -> Expression:
        left = self.expr_aditiva()
        while self.check(
            TokenType.OP_MENOR, TokenType.OP_MENOR_IG,
            TokenType.OP_MAYOR, TokenType.OP_MAYOR_IG
        ):
            op_tok = self.current()
            self.match(
                TokenType.OP_MENOR, TokenType.OP_MENOR_IG,
                TokenType.OP_MAYOR, TokenType.OP_MAYOR_IG
            )
            right = self.expr_aditiva()
            left = RelationalExpr(left, op_tok, right)
        return left

    # ExprAditiva → Term ( (OP_SUMA | OP_RESTA) Term )*
    def expr_aditiva(self) -> Expression:
        left = self.term()
        while self.check(TokenType.OP_SUMA, TokenType.OP_RESTA):
            op_tok = self.current()
            self.match(TokenType.OP_SUMA, TokenType.OP_RESTA)
            right = self.term()
            left = BinaryExpr(left, op_tok, right)
        return left

    # Term → Factor ( (OP_MULT | OP_DIV | OP_MOD) Factor )*
    def term(self) -> Expression:
        left = self.factor()
        while self.check(TokenType.OP_MULT, TokenType.OP_DIV, TokenType.OP_MOD):
            op_tok = self.current()
            self.match(TokenType.OP_MULT, TokenType.OP_DIV, TokenType.OP_MOD)
            right = self.factor()
            left = BinaryExpr(left, op_tok, right)
        return left

    # Factor → OP_NOT Factor | OP_RESTA Factor | OP_INC ExprPostfija | OP_DEC ExprPostfija | ExprPostfija
    def factor(self) -> Expression:
        if self.match(TokenType.OP_NOT):
            op_tok = self.tokens[self.pos - 1]
            operand = self.factor()
            return UnaryExpr(op_tok, operand, is_prefix=True)
        elif self.match(TokenType.OP_RESTA):
            op_tok = self.tokens[self.pos - 1]
            operand = self.factor()
            return UnaryExpr(op_tok, operand, is_prefix=True)
        elif self.match(TokenType.OP_INC):
            op_tok = self.tokens[self.pos - 1]
            operand = self.expr_postfija()
            return UnaryExpr(op_tok, operand, is_prefix=True)
        elif self.match(TokenType.OP_DEC):
            op_tok = self.tokens[self.pos - 1]
            operand = self.expr_postfija()
            return UnaryExpr(op_tok, operand, is_prefix=True)
        else:
            return self.expr_postfija()

    # ExprPostfija → ExprPrimaria (OP_INC | OP_DEC)?
    def expr_postfija(self) -> Expression:
        expr_node = self.expr_primaria()
        
        if self.match(TokenType.OP_INC):
            op_tok = self.tokens[self.pos - 1]
            return PostfixExpr(expr_node, op_tok)
        elif self.match(TokenType.OP_DEC):
            op_tok = self.tokens[self.pos - 1]
            return PostfixExpr(expr_node, op_tok)
        
        return expr_node

    # ExprPrimaria → id | literal | '(' Expr ')' | id '(' [args] ')' | id '[' Expr ']'
    def expr_primaria(self) -> Expression:
        # Literales
        if self.match(
            TokenType.NUM_INT, TokenType.NUM_FLOAT,
            TokenType.STRING, TokenType.CHAR_LITERAL,
            TokenType.TRUE, TokenType.FALSE
        ):
            lit_tok = self.tokens[self.pos - 1]
            return LiteralExpr(lit_tok)
        
        # Identificador (puede ser var, func call, o array access)
        if self.match(TokenType.ID):
            id_tok = self.tokens[self.pos - 1]
            
            # Llamada a función
            if self.match(TokenType.PAREN_IZQ):
                args = []
                if not self.check(TokenType.PAREN_DER):
                    args = self.lista_args()
                self.consume(TokenType.PAREN_DER, "Expected ')' after function arguments")
                return CallExpr(id_tok, args)
            
            # Acceso a arreglo
            elif self.match(TokenType.CORCHETE_IZQ):
                index_expr = self.expr()
                self.consume(TokenType.CORCHETE_DER, "Expected ']' after array index")
                return IndexExpr(id_tok, index_expr)
            
            # Solo identificador
            else:
                return IdentifierExpr(id_tok)
        
        # Expresión agrupada
        if self.match(TokenType.PAREN_IZQ):
            expr_node = self.expr()
            self.consume(TokenType.PAREN_DER, "Expected ')' after expression")
            return GroupingExpr(expr_node)
        
        tok = self.current()
        raise ParserError(
            f"[L{tok.line},C{tok.column}] Invalid expression start: "
            f"{tok.type} ({tok.lexeme!r})"
        )

    # ListaArgs → Expr | Expr COMA ListaArgs
    def lista_args(self) -> List[Expression]:
        args = [self.expr()]
        while self.match(TokenType.COMA):
            args.append(self.expr())
        return args

    def es_inicio_expr(self):
        return self.check(
            TokenType.NUM_INT, TokenType.NUM_FLOAT,
            TokenType.STRING, TokenType.CHAR_LITERAL,
            TokenType.TRUE, TokenType.FALSE,
            TokenType.ID, TokenType.PAREN_IZQ,
            TokenType.OP_NOT, TokenType.OP_RESTA,
            TokenType.OP_INC, TokenType.OP_DEC
        )
