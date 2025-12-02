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
    """Declaración de variable: tipo id [= expr] [, id [= expr]]*"""
    type_token: Token  # Token del tipo (int, float, etc.)
    declarations: List['VarDeclItem']  # Lista de (id_token, init_expr)

    def __repr__(self):
        return f"VarDecl({self.type_token.lexeme}, {len(self.declarations)} items)"


@dataclass
class VarDeclItem:
    """Un item en una declaración de variables: id [= expr]"""
    id_token: Token  # Token del identificador
    initializer: Optional['Expression']  # None si no hay inicializador


@dataclass
class FuncDecl(Declaration):
    """Declaración de función: tipo id ( [parametros] ) bloque"""
    return_type: Token  # Token del tipo de retorno
    name_token: Token  # Token del nombre de la función
    parameters: List['Parameter']  # Lista de parámetros
    body: 'BlockStmt'  # Cuerpo de la función


@dataclass
class Parameter:
    """Un parámetro de función: tipo id"""
    type_token: Token
    name_token: Token


@dataclass
class ClassDecl(Declaration):
    """Declaración de clase: class id { [miembros] }"""
    name_token: Token
    members: List['ClassMember']  # Métodos y variables de clase


@dataclass
class ClassMember:
    """Un miembro de clase (variable o método)"""
    access_modifier: Optional[Token]  # PUBLIC, PRIVATE, o None (default private)
    declaration: 'Declaration'  # VarDecl o FuncDecl


# ===== SENTENCIAS =====

@dataclass
class Statement:
    """Clase base abstracta para sentencias"""
    pass


@dataclass
class ExprStmt(Statement):
    """Sentencia de expresión: expr;"""
    expression: Optional['Expression']  # None si es solo `;`

    def __repr__(self):
        return f"ExprStmt({self.expression})"


@dataclass
class BlockStmt(Statement):
    """Bloque de sentencias: { sentencias }"""
    statements: List[Statement]

    def __repr__(self):
        return f"BlockStmt({len(self.statements)} stmts)"


@dataclass
class IfStmt(Statement):
    """Sentencia if/else: if (expr) sentencia [else sentencia]"""
    condition: 'Expression'
    then_stmt: Statement
    else_stmt: Optional[Statement]

    def __repr__(self):
        return f"IfStmt(cond={self.condition})"


@dataclass
class WhileStmt(Statement):
    """Sentencia while: while (expr) sentencia"""
    condition: 'Expression'
    body: Statement

    def __repr__(self):
        return f"WhileStmt(cond={self.condition})"


@dataclass
class ForStmt(Statement):
    """Sentencia for: for (init; cond; update) sentencia"""
    init: Optional['Expression']  # O None, o DeclVar, o Expr
    condition: Optional['Expression']
    update: Optional['Expression']
    body: Statement

    def __repr__(self):
        return f"ForStmt()"


@dataclass
class SwitchStmt(Statement):
    """Sentencia switch: switch (expr) { casos }"""
    expr: 'Expression'
    cases: List['CaseStmt']

    def __repr__(self):
        return f"SwitchStmt({len(self.cases)} cases)"


@dataclass
class CaseStmt:
    """Un case dentro de switch: case expr: sentencias; o default: sentencias;"""
    case_expr: Optional['Expression']  # None si es default
    statements: List[Statement]
    is_default: bool = False

    def __repr__(self):
        return f"CaseStmt(default={self.is_default})"


@dataclass
class ReturnStmt(Statement):
    """Sentencia return: return [expr];"""
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
    """Expresión de asignación: id = expr"""
    target_token: Token  # Token del identificador
    value: Expression

    def __repr__(self):
        return f"AssignExpr({self.target_token.lexeme} = ...)"


@dataclass
class BinaryExpr(Expression):
    """Expresión binaria: left op right"""
    left: Expression
    operator: Token  # Token del operador
    right: Expression

    def __repr__(self):
        return f"BinaryExpr({self.operator.type})"


@dataclass
class UnaryExpr(Expression):
    """Expresión unaria: op expr (!, -, ++, --)"""
    operator: Token  # Token del operador
    operand: Expression
    is_postfix: bool = False  # True si es ++ o -- postfijo

    def __repr__(self):
        return f"UnaryExpr({self.operator.type}, postfix={self.is_postfix})"


@dataclass
class CallExpr(Expression):
    """Llamada a función: id ( [args] )"""
    func_token: Token  # Token del nombre de la función
    arguments: List[Expression]

    def __repr__(self):
        return f"CallExpr({self.func_token.lexeme})"


@dataclass
class IndexExpr(Expression):
    """Acceso a arreglo: id [ expr ]"""
    array_token: Token  # Token del identificador del arreglo
    index: Expression

    def __repr__(self):
        return f"IndexExpr({self.array_token.lexeme})"


@dataclass
class LiteralExpr(Expression):
    """Literal: número, string, char, true, false"""
    value_token: Token  # Token que contiene el literal

    def __repr__(self):
        return f"LiteralExpr({self.value_token.type})"


@dataclass
class IdentifierExpr(Expression):
    """Identificador (variable, función, etc.)"""
    id_token: Token

    def __repr__(self):
        return f"IdentifierExpr({self.id_token.lexeme})"


@dataclass
class GroupingExpr(Expression):
    """Expresión agrupada: ( expr )"""
    expression: Expression

    def __repr__(self):
        return f"GroupingExpr(...)"
