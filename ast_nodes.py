# ast_nodes.py
from dataclasses import dataclass
from typing import List, Optional
from tokens import Token


# ===== NODOS RAÍZ =====

@dataclass
class Program:
    """Nodo raíz del programa"""
    declarations: List['Declaration']


# ===== DECLARACIONES =====

@dataclass
class Declaration:
    """Clase base abstracta para declaraciones"""
    pass


@dataclass
class VarDecl(Declaration):
    """DECLVAR: TIPO LISTAID punto_coma"""
    type_token: Token  # Token del tipo (int, float, etc.)
    declarators: List['VarDeclarator']  # Lista de (id_token, init_expr)

    def __repr__(self):
        return f"VarDecl({self.type_token.lexeme}, {len(self.declarators)} declarators)"


@dataclass
class VarDeclarator:
    """Un item en LISTAID: id INICIALIZACION"""
    name_token: Token  # Token del identificador
    initializer: Optional['Expression']  # None si no hay inicializador
    is_array: bool = False  # True si es un arreglo


@dataclass
class VarDeclSinPunto(Declaration):
    """DECLVARSINPUNTO: TIPO LISTAID (sin punto y coma, para for init)"""
    type_token: Token
    declarators: List['VarDeclarator']


@dataclass
class FuncDecl(Declaration):
    """DECLFUNC: TIPO id paren_izq PARAMETROS paren_der BLOQUE"""
    return_type: Token  # Token del tipo de retorno
    name_token: Token  # Token del nombre de la función
    parameters: List['Param']  # Lista de parámetros
    body: 'BlockStmt'  # Cuerpo de la función


@dataclass
class Param:
    """PARAM: TIPO id"""
    type_token: Token
    name_token: Token


@dataclass
class ClassDecl(Declaration):
    """DECLCLASE: class id llave_izq LISTAMIEMBROS llave_der"""
    name_token: Token
    members: List['ClassMember']  # Métodos y variables de clase


@dataclass
class ClassMember:
    """MIEMBRO: MODIFICADORACCESO DECLVAR | MODIFICADORACCESO DECLFUNC"""
    access_modifier: Optional[Token]  # PUBLIC, PRIVATE, o None (default private)
    declaration: 'Declaration'  # VarDecl o FuncDecl


# ===== SENTENCIAS =====

@dataclass
class Statement:
    """Clase base abstracta para sentencias"""
    pass


@dataclass
class ExprStmt(Statement):
    """SENTENCIAEXPR: EXPR punto_coma | punto_coma"""
    expression: Optional['Expression']  # None si es solo `;`

    def __repr__(self):
        return f"ExprStmt({self.expression})"


@dataclass
class BlockStmt(Statement):
    """BLOQUE: llave_izq LISTASENTENCIAS llave_der"""
    statements: List[Statement]

    def __repr__(self):
        return f"BlockStmt({len(self.statements)} stmts)"


@dataclass
class IfStmt(Statement):
    """SENTENCIASEL: if paren_izq EXPR paren_der SENTENCIA [else SENTENCIA]"""
    condition: 'Expression'
    then_stmt: Statement
    else_stmt: Optional[Statement]

    def __repr__(self):
        return f"IfStmt(cond={self.condition})"


@dataclass
class WhileStmt(Statement):
    """SENTENCIAITER: while paren_izq EXPR paren_der SENTENCIA"""
    condition: 'Expression'
    body: Statement

    def __repr__(self):
        return f"WhileStmt(cond={self.condition})"


@dataclass
class VarDeclStmt(Statement):
    """Variable declaration within statements (int x = 0;)"""
    var_decl: 'VarDecl'

    def __repr__(self):
        return f"VarDeclStmt({self.var_decl})"


@dataclass
class ForStmt(Statement):
    """SENTENCIAITER: for paren_izq FORINIT punto_coma EXPR punto_coma FORUPDATE paren_der SENTENCIA"""
    init: Optional['Declaration | Expression']  # DECLVARSINPUNTO o EXPR o ε
    condition: Optional['Expression']  # EXPR o ε
    update: Optional['Expression']  # FORUPDATE (EXPR o ε)
    body: Statement

    def __repr__(self):
        return f"ForStmt()"


@dataclass
class SwitchStmt(Statement):
    """SENTENCIASWITCH: switch paren_izq EXPR paren_der llave_izq LISTACASOS llave_der"""
    expr: 'Expression'
    cases: List['CaseStmt']

    def __repr__(self):
        return f"SwitchStmt({len(self.cases)} cases)"


@dataclass
class CaseStmt:
    """CASO: case EXPR punto_coma LISTASENTENCIAS | default punto_coma LISTASENTENCIAS"""
    case_expr: Optional['Expression']  # None si es default
    statements: List[Statement]

    def __repr__(self):
        return f"CaseStmt(default={self.case_expr is None})"


@dataclass
class ReturnStmt(Statement):
    """SENTENCIARET: return EXPR punto_coma | return punto_coma"""
    return_expr: Optional['Expression']

    def __repr__(self):
        return f"ReturnStmt({self.return_expr})"


# ===== EXPRESIONES =====

@dataclass
class Expression:
    """Clase base abstracta para expresiones"""
    pass


@dataclass
class AssignExpr(Expression):
    """EXPRASIGNACION': op_asig EXPRASIGNACION (derecha-asociativa)"""
    target: Expression  # IdentifierExpr o IndexExpr
    value: Expression

    def __repr__(self):
        return f"AssignExpr({self.target} = ...)"


@dataclass
class LogicalOrExpr(Expression):
    """EXPRLOGICA': op_or EXPRAND EXPRLOGICA'"""
    left: Expression
    operator: Token  # OP_OR
    right: Expression

    def __repr__(self):
        return f"LogicalOrExpr({self.operator.type})"


@dataclass
class LogicalAndExpr(Expression):
    """EXPRAND': op_and EXPRIGUALDAD EXPRAND'"""
    left: Expression
    operator: Token  # OP_AND
    right: Expression

    def __repr__(self):
        return f"LogicalAndExpr({self.operator.type})"


@dataclass
class EqualityExpr(Expression):
    """EXPRIGUALDAD': (op_igual | op_distinto) EXPRRELACIONAL"""
    left: Expression
    operator: Token  # OP_IGUAL o OP_DISTINTO
    right: Expression

    def __repr__(self):
        return f"EqualityExpr({self.operator.type})"


@dataclass
class RelationalExpr(Expression):
    """EXPRRELACIONAL': (op_menor | op_menor_ig | op_mayor | op_mayor_ig) EXPRADITIVA"""
    left: Expression
    operator: Token  # OP_MENOR, OP_MENOR_IG, OP_MAYOR, OP_MAYOR_IG
    right: Expression

    def __repr__(self):
        return f"RelationalExpr({self.operator.type})"


@dataclass
class BinaryExpr(Expression):
    """Expresión binaria: +, -, *, /, %"""
    left: Expression
    operator: Token  # Operador: OP_SUMA, OP_RESTA, OP_MULT, OP_DIV, OP_MOD
    right: Expression

    def __repr__(self):
        return f"BinaryExpr({self.operator.type})"


@dataclass
class UnaryExpr(Expression):
    """FACTOR: op_not, op_resta (prefijo); ++expr, --expr (prefijo)"""
    operator: Token  # OP_NOT, OP_RESTA, OP_INC, OP_DEC
    operand: Expression
    is_prefix: bool = True  # True para prefijo

    def __repr__(self):
        return f"UnaryExpr({self.operator.type}, prefix={self.is_prefix})"


@dataclass
class PostfixExpr(Expression):
    """EXPRPOSTFIJA': expr++ o expr--"""
    operand: Expression
    operator: Token  # OP_INC o OP_DEC

    def __repr__(self):
        return f"PostfixExpr({self.operator.type})"


@dataclass
class CallExpr(Expression):
    """LLAMADAFUNC: id paren_izq ARGSOPTS paren_der"""
    func_token: Token  # Token del nombre de la función
    arguments: List[Expression]

    def __repr__(self):
        return f"CallExpr({self.func_token.lexeme})"


@dataclass
class IndexExpr(Expression):
    """ACCESOARREGLO: id corchete_izq EXPR corchete_der"""
    array_token: Token  # Token del identificador del arreglo
    index: Expression

    def __repr__(self):
        return f"IndexExpr({self.array_token.lexeme})"


@dataclass
class LiteralExpr(Expression):
    """LITERAL: num_int, num_float, num_exp, string, char, true, false"""
    value_token: Token  # Token que contiene el literal

    def __repr__(self):
        return f"LiteralExpr({self.value_token.type})"


@dataclass
class IdentifierExpr(Expression):
    """EXPRPRIMARIA: id"""
    id_token: Token

    def __repr__(self):
        return f"IdentifierExpr({self.id_token.lexeme})"


@dataclass
class GroupingExpr(Expression):
    """EXPRPRIMARIA: paren_izq EXPR paren_der"""
    expression: Expression

    def __repr__(self):
        return f"GroupingExpr(...)"
