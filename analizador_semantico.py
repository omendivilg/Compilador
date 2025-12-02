# analizador_semantico.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from ast_nodes import *
from tokens import TokenType


class TypeKind(Enum):
    """Tipos primitivos soportados"""
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    CHAR = "char"
    BOOL = "bool"
    VOID = "void"
    ERROR = "error"  # Para errores de tipo

    def __repr__(self):
        return self.value


@dataclass
class Symbol:
    """Entrada en la tabla de símbolos"""
    name: str
    type_: TypeKind
    kind: str  # "variable", "function", "class", "parameter"
    token: Token
    scope_level: int
    is_initialized: bool = False
    is_array: bool = False  # True si es un arreglo

    # Atributos adicionales para funciones
    param_types: Optional[List[TypeKind]] = None
    return_type: Optional[TypeKind] = None

    # Atributos para clases
    members: Optional[Dict[str, 'Symbol']] = None
    methods: Optional[Dict[str, 'Symbol']] = None


class SemanticError(Exception):
    """Excepción para errores semánticos"""
    pass


class Scope:
    """Representa un scope (nivel de visibilidad)"""
    def __init__(self, scope_type: str, parent: Optional['Scope'] = None):
        self.scope_type = scope_type  # "global", "class", "function", "block"
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.level = parent.level + 1 if parent else 0

    def define(self, name: str, symbol: Symbol):
        """Define un símbolo en este scope"""
        if name in self.symbols:
            raise SemanticError(
                f"[L{symbol.token.line},C{symbol.token.column}] "
                f"Symbol '{name}' already defined in this scope"
            )
        self.symbols[name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo en este scope y sus antecesores"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo solo en este scope"""
        return self.symbols.get(name)


class TypeSystem:
    """Sistema de tipos con reglas de compatibilidad"""

    @staticmethod
    def get_literal_type(token: Token) -> TypeKind:
        """Infiere el tipo de un literal"""
        if token.type == TokenType.NUM_INT:
            return TypeKind.INT
        elif token.type == TokenType.NUM_FLOAT:
            return TypeKind.FLOAT
        elif token.type == TokenType.STRING:
            return TypeKind.ERROR  # String no es tipo primitivo en este lenguaje
        elif token.type == TokenType.CHAR_LITERAL:
            return TypeKind.CHAR
        elif token.type == TokenType.TRUE or token.type == TokenType.FALSE:
            return TypeKind.BOOL
        else:
            return TypeKind.ERROR

    @staticmethod
    def is_numeric(type_: TypeKind) -> bool:
        """Verifica si un tipo es numérico"""
        return type_ in [TypeKind.INT, TypeKind.FLOAT, TypeKind.DOUBLE, TypeKind.CHAR]

    @staticmethod
    def is_assignable(target: TypeKind, source: TypeKind) -> bool:
        """Verifica si se puede asignar source a target"""
        if target == source:
            return True
        # Permitir conversiones numéricas implícitas
        if TypeSystem.is_numeric(target) and TypeSystem.is_numeric(source):
            return True
        if target == TypeKind.ERROR or source == TypeKind.ERROR:
            return True
        return False

    @staticmethod
    def is_compatible_for_op(left: TypeKind, right: TypeKind, op_type: str) -> bool:
        """Verifica compatibilidad de tipos para operadores"""
        if op_type in ["arithmetic", "comparison"]:
            return TypeSystem.is_numeric(left) and TypeSystem.is_numeric(right)
        elif op_type == "logical":
            return (left == TypeKind.BOOL and right == TypeKind.BOOL) or \
                   (left == TypeKind.ERROR or right == TypeKind.ERROR)
        elif op_type == "unary_logical":
            return left == TypeKind.BOOL or left == TypeKind.ERROR
        elif op_type == "unary_arithmetic":
            return TypeSystem.is_numeric(left) or left == TypeKind.ERROR
        return True


class SemanticAnalyzer:
    """Analizador semántico con patrón Visitor"""

    def __init__(self):
        self.current_scope: Optional[Scope] = None
        self.global_scope: Optional[Scope] = None
        self.current_function: Optional[Symbol] = None
        self.current_class: Optional[Symbol] = None
        self.errors: List[str] = []
        self.type_system = TypeSystem()

    def analyze(self, program: Program) -> List[str]:
        """Entrada principal del análisis semántico"""
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope

        try:
            self.visit_Program(program)
        except SemanticError as e:
            self.errors.append(str(e))

        return self.errors

    # ===== VISITORS: Programa y Declaraciones =====

    def visit_Program(self, node: Program):
        """Análisis de programa"""
        # Primera pasada: colectar declaraciones de nivel superior
        for decl in node.declarations:
            self.collect_declaration(decl)

        # Segunda pasada: verificar cuerpos
        for decl in node.declarations:
            self.visit_Declaration(decl)

    def collect_declaration(self, node: Declaration):
        """Pre-procesa declaraciones para registrar símbolos"""
        if isinstance(node, VarDecl):
            # Las variables globales se registran más tarde en visit_VarDecl
            pass
        elif isinstance(node, FuncDecl):
            self.collect_FuncDecl(node)
        elif isinstance(node, ClassDecl):
            self.collect_ClassDecl(node)

    def collect_FuncDecl(self, node: FuncDecl):
        """Colecta firma de función"""
        func_name = node.name_token.lexeme
        return_type = self.token_to_type(node.return_type)

        param_types = [self.token_to_type(p.type_token) for p in node.parameters]

        sym = Symbol(
            name=func_name,
            type_=return_type,
            kind="function",
            token=node.name_token,
            scope_level=self.current_scope.level,
            param_types=param_types,
            return_type=return_type
        )

        try:
            self.current_scope.define(func_name, sym)
        except SemanticError as e:
            self.errors.append(str(e))

    def collect_ClassDecl(self, node: ClassDecl):
        """Colecta declaración de clase"""
        class_name = node.name_token.lexeme

        sym = Symbol(
            name=class_name,
            type_=TypeKind.ERROR,  # Las clases no tienen tipo primitivo
            kind="class",
            token=node.name_token,
            scope_level=self.current_scope.level,
            members={},
            methods={}
        )

        try:
            self.current_scope.define(class_name, sym)
        except SemanticError as e:
            self.errors.append(str(e))

    def visit_Declaration(self, node: Declaration):
        """Visitor genérico para declaraciones"""
        if isinstance(node, VarDecl):
            self.visit_VarDecl(node)
        elif isinstance(node, FuncDecl):
            self.visit_FuncDecl(node)
        elif isinstance(node, ClassDecl):
            self.visit_ClassDecl(node)

    def visit_VarDecl(self, node: VarDecl):
        """Analiza declaración de variable"""
        var_type = self.token_to_type(node.type_token)

        # VOID solo permitido en funciones
        if var_type == TypeKind.VOID:
            self.errors.append(
                f"[L{node.type_token.line},C{node.type_token.column}] "
                f"Variable cannot have type 'void'"
            )
            return

        for item in node.declarations:
            var_name = item.id_token.lexeme

            sym = Symbol(
                name=var_name,
                type_=var_type,
                kind="variable",
                token=item.id_token,
                scope_level=self.current_scope.level,
                is_initialized=item.initializer is not None,
                is_array=item.is_array
            )

            try:
                self.current_scope.define(var_name, sym)
            except SemanticError as e:
                self.errors.append(str(e))
                continue

            # Verificar inicializador si existe
            if item.initializer:
                init_type = self.visit_Expression(item.initializer)
                if not self.type_system.is_assignable(var_type, init_type):
                    self.errors.append(
                        f"[L{item.id_token.line},C{item.id_token.column}] "
                        f"Cannot assign {init_type} to {var_type}"
                    )

    def visit_FuncDecl(self, node: FuncDecl):
        """Analiza declaración de función"""
        func_name = node.name_token.lexeme

        # Crear nuevo scope para la función
        prev_scope = self.current_scope
        self.current_scope = Scope("function", prev_scope)
        prev_function = self.current_function
        self.current_function = prev_scope.lookup(func_name)

        try:
            # Registrar parámetros en el scope de la función
            for param in node.parameters:
                param_type = self.token_to_type(param.type_token)
                if param_type == TypeKind.VOID:
                    self.errors.append(
                        f"[L{param.type_token.line},C{param.type_token.column}] "
                        f"Parameter cannot have type 'void'"
                    )
                    continue

                param_sym = Symbol(
                    name=param.name_token.lexeme,
                    type_=param_type,
                    kind="parameter",
                    token=param.name_token,
                    scope_level=self.current_scope.level,
                    is_initialized=True
                )
                try:
                    self.current_scope.define(param.name_token.lexeme, param_sym)
                except SemanticError as e:
                    self.errors.append(str(e))

            # Analizar el cuerpo
            self.visit_BlockStmt(node.body)

        finally:
            self.current_scope = prev_scope
            self.current_function = prev_function

    def visit_ClassDecl(self, node: ClassDecl):
        """Analiza declaración de clase"""
        class_name = node.name_token.lexeme
        class_sym = self.current_scope.lookup(class_name)

        # Crear nuevo scope para la clase
        prev_scope = self.current_scope
        self.current_scope = Scope("class", prev_scope)
        prev_class = self.current_class
        self.current_class = class_sym

        try:
            for member in node.members:
                # Colectar miembros primero
                if isinstance(member.declaration, VarDecl):
                    # Registrar variable de miembro
                    for item in member.declaration.declarations:
                        var_sym = Symbol(
                            name=item.id_token.lexeme,
                            type_=self.token_to_type(member.declaration.type_token),
                            kind="variable",
                            token=item.id_token,
                            scope_level=self.current_scope.level
                        )
                        try:
                            self.current_scope.define(item.id_token.lexeme, var_sym)
                            if class_sym and class_sym.members is not None:
                                class_sym.members[item.id_token.lexeme] = var_sym
                        except SemanticError as e:
                            self.errors.append(str(e))

                elif isinstance(member.declaration, FuncDecl):
                    # Registrar método
                    func_sym = Symbol(
                        name=member.declaration.name_token.lexeme,
                        type_=self.token_to_type(member.declaration.return_type),
                        kind="function",
                        token=member.declaration.name_token,
                        scope_level=self.current_scope.level,
                        param_types=[self.token_to_type(p.type_token) for p in member.declaration.parameters],
                        return_type=self.token_to_type(member.declaration.return_type)
                    )
                    try:
                        self.current_scope.define(member.declaration.name_token.lexeme, func_sym)
                        if class_sym and class_sym.methods is not None:
                            class_sym.methods[member.declaration.name_token.lexeme] = func_sym
                    except SemanticError as e:
                        self.errors.append(str(e))

            # Segunda pasada: analizar cuerpos de métodos
            for member in node.members:
                if isinstance(member.declaration, FuncDecl):
                    self.visit_FuncDecl(member.declaration)

        finally:
            self.current_scope = prev_scope
            self.current_class = prev_class

    # ===== VISITORS: Sentencias =====

    def visit_Statement(self, node: Statement):
        """Visitor genérico para sentencias"""
        if isinstance(node, ExprStmt):
            self.visit_ExprStmt(node)
        elif isinstance(node, VarDeclStmt):
            self.visit_VarDeclStmt(node)
        elif isinstance(node, BlockStmt):
            self.visit_BlockStmt(node)
        elif isinstance(node, IfStmt):
            self.visit_IfStmt(node)
        elif isinstance(node, WhileStmt):
            self.visit_WhileStmt(node)
        elif isinstance(node, ForStmt):
            self.visit_ForStmt(node)
        elif isinstance(node, SwitchStmt):
            self.visit_SwitchStmt(node)
        elif isinstance(node, ReturnStmt):
            self.visit_ReturnStmt(node)

    def visit_ExprStmt(self, node: ExprStmt):
        """Analiza sentencia de expresión"""
        if node.expression:
            self.visit_Expression(node.expression)

    def visit_VarDeclStmt(self, node: VarDeclStmt):
        """Analiza sentencia de declaración de variable"""
        self.visit_VarDecl(node.var_decl)

    def visit_BlockStmt(self, node: BlockStmt):
        """Analiza bloque de sentencias"""
        # Crear nuevo scope para el bloque
        prev_scope = self.current_scope
        self.current_scope = Scope("block", prev_scope)

        try:
            for stmt in node.statements:
                self.visit_Statement(stmt)
        finally:
            self.current_scope = prev_scope

    def visit_IfStmt(self, node: IfStmt):
        """Analiza sentencia if"""
        cond_type = self.visit_Expression(node.condition)
        if cond_type != TypeKind.BOOL and cond_type != TypeKind.ERROR:
            cond_line = self._get_node_line(node.condition)
            self.errors.append(
                f"[L{cond_line}] "
                f"Condition must be boolean, got {cond_type}"
            )

        self.visit_Statement(node.then_stmt)
        if node.else_stmt:
            self.visit_Statement(node.else_stmt)

    def visit_WhileStmt(self, node: WhileStmt):
        """Analiza sentencia while"""
        cond_type = self.visit_Expression(node.condition)
        if cond_type != TypeKind.BOOL and cond_type != TypeKind.ERROR:
            cond_line = self._get_node_line(node.condition)
            self.errors.append(
                f"[L{cond_line}] "
                f"Condition must be boolean, got {cond_type}"
            )

        self.visit_Statement(node.body)

    def visit_ForStmt(self, node: ForStmt):
        """Analiza sentencia for"""
        # Crear scope para el for
        prev_scope = self.current_scope
        self.current_scope = Scope("block", prev_scope)

        try:
            if node.init:
                # Init puede ser una VarDecl o una Expression
                if isinstance(node.init, VarDecl):
                    self.visit_VarDecl(node.init)
                else:
                    self.visit_Expression(node.init)
            
            if node.condition:
                cond_type = self.visit_Expression(node.condition)
                if cond_type != TypeKind.BOOL and cond_type != TypeKind.ERROR:
                    cond_line = self._get_node_line(node.condition)
                    self.errors.append(
                        f"[L{cond_line}] "
                        f"Condition must be boolean, got {cond_type}"
                    )
            if node.update:
                self.visit_Expression(node.update)

            self.visit_Statement(node.body)
        finally:
            self.current_scope = prev_scope

    def visit_SwitchStmt(self, node: SwitchStmt):
        """Analiza sentencia switch"""
        switch_type = self.visit_Expression(node.expr)

        for case in node.cases:
            if case.case_expr and not case.is_default:
                case_type = self.visit_Expression(case.case_expr)
                if not self.type_system.is_assignable(switch_type, case_type):
                    case_line = self._get_node_line(case.case_expr)
                    self.errors.append(
                        f"[L{case_line}] "
                        f"Case type {case_type} not compatible with switch type {switch_type}"
                    )

            for stmt in case.statements:
                self.visit_Statement(stmt)

    def visit_ReturnStmt(self, node: ReturnStmt):
        """Analiza sentencia return"""
        if self.current_function is None:
            ret_line = self._get_node_line(node.return_expr) if node.return_expr else 0
            self.errors.append(
                f"[L{ret_line}] "
                f"Return outside function"
            )
            return

        expected_return = self.current_function.return_type
        if node.return_expr is None:
            if expected_return != TypeKind.VOID:
                self.errors.append(
                    f"Function expects return type {expected_return}, got void"
                )
        else:
            actual_return = self.visit_Expression(node.return_expr)
            if not self.type_system.is_assignable(expected_return, actual_return):
                ret_line = self._get_node_line(node.return_expr)
                self.errors.append(
                    f"[L{ret_line}] "
                    f"Cannot return {actual_return} from function expecting {expected_return}"
                )

    # ===== VISITORS: Expresiones =====

    def visit_Expression(self, node: Expression) -> TypeKind:
        """Visitor genérico para expresiones - retorna el tipo"""
        if isinstance(node, AssignExpr):
            return self.visit_AssignExpr(node)
        elif isinstance(node, BinaryExpr):
            return self.visit_BinaryExpr(node)
        elif isinstance(node, UnaryExpr):
            return self.visit_UnaryExpr(node)
        elif isinstance(node, CallExpr):
            return self.visit_CallExpr(node)
        elif isinstance(node, IndexExpr):
            return self.visit_IndexExpr(node)
        elif isinstance(node, LiteralExpr):
            return self.visit_LiteralExpr(node)
        elif isinstance(node, IdentifierExpr):
            return self.visit_IdentifierExpr(node)
        elif isinstance(node, GroupingExpr):
            return self.visit_GroupingExpr(node)
        return TypeKind.ERROR

    def visit_AssignExpr(self, node: AssignExpr) -> TypeKind:
        """Analiza expresión de asignación"""
        # Verifica que el target sea válido (IdentifierExpr o IndexExpr)
        if not isinstance(node.target, (IdentifierExpr, IndexExpr)):
            self.errors.append(
                f"[L{self._get_node_line(node.target)}] Invalid assignment target"
            )
            return TypeKind.ERROR
        
        if isinstance(node.target, IdentifierExpr):
            # Asignación simple: id = expr
            target_name = node.target.id_token.lexeme
            target_sym = self.current_scope.lookup(target_name)

            if target_sym is None:
                self.errors.append(
                    f"[L{node.target.id_token.line},C{node.target.id_token.column}] "
                    f"Undefined variable '{target_name}'"
                )
                return TypeKind.ERROR

            value_type = self.visit_Expression(node.value)
            
            if not self.type_system.is_assignable(target_sym.type_, value_type):
                self.errors.append(
                    f"[L{node.target.id_token.line},C{node.target.id_token.column}] "
                    f"Cannot assign {value_type} to {target_sym.type_}"
                )
                return TypeKind.ERROR
            
            node.expr_type = target_sym.type_
            return target_sym.type_
        
        elif isinstance(node.target, IndexExpr):
            # Asignación a índice: arr[idx] = expr
            arr_name = node.target.array_token.lexeme
            arr_sym = self.current_scope.lookup(arr_name)
            
            if arr_sym is None:
                self.errors.append(
                    f"[L{node.target.array_token.line},C{node.target.array_token.column}] "
                    f"Undefined array '{arr_name}'"
                )
                return TypeKind.ERROR
            
            if not arr_sym.is_array:
                self.errors.append(
                    f"[L{node.target.array_token.line},C{node.target.array_token.column}] "
                    f"'{arr_name}' is not an array"
                )
                return TypeKind.ERROR
            
            # Verifica el índice
            index_type = self.visit_Expression(node.target.index)
            if index_type != TypeKind.INT:
                self.errors.append(
                    f"[L{self._get_node_line(node.target.index)}] "
                    f"Array index must be INT, got {index_type}"
                )
            
            value_type = self.visit_Expression(node.value)
            
            if not self.type_system.is_assignable(arr_sym.type_, value_type):
                self.errors.append(
                    f"[L{node.target.array_token.line},C{node.target.array_token.column}] "
                    f"Cannot assign {value_type} to array element type {arr_sym.type_}"
                )
                return TypeKind.ERROR
            
            node.expr_type = arr_sym.type_
            return arr_sym.type_

        return target_sym.type_

    def visit_BinaryExpr(self, node: BinaryExpr) -> TypeKind:
        """Analiza expresión binaria"""
        left_type = self.visit_Expression(node.left)
        right_type = self.visit_Expression(node.right)

        op_type = node.operator.type

        if op_type in [TokenType.OP_SUMA, TokenType.OP_RESTA, TokenType.OP_MULT, TokenType.OP_DIV, TokenType.OP_MOD]:
            if not self.type_system.is_compatible_for_op(left_type, right_type, "arithmetic"):
                self.errors.append(
                    f"[L{node.operator.line},C{node.operator.column}] "
                    f"Invalid operands for {node.operator.lexeme}: {left_type} and {right_type}"
                )
            return left_type if left_type != TypeKind.ERROR else right_type

        elif op_type in [TokenType.OP_MENOR, TokenType.OP_MENOR_IG, TokenType.OP_MAYOR, TokenType.OP_MAYOR_IG,
                         TokenType.OP_IGUAL, TokenType.OP_DISTINTO]:
            if not self.type_system.is_compatible_for_op(left_type, right_type, "comparison"):
                self.errors.append(
                    f"[L{node.operator.line},C{node.operator.column}] "
                    f"Invalid operands for {node.operator.lexeme}: {left_type} and {right_type}"
                )
            return TypeKind.BOOL

        elif op_type in [TokenType.OP_AND, TokenType.OP_OR]:
            if not self.type_system.is_compatible_for_op(left_type, right_type, "logical"):
                self.errors.append(
                    f"[L{node.operator.line},C{node.operator.column}] "
                    f"Invalid operands for {node.operator.lexeme}: {left_type} and {right_type}"
                )
            return TypeKind.BOOL

        return TypeKind.ERROR

    def visit_UnaryExpr(self, node: UnaryExpr) -> TypeKind:
        """Analiza expresión unaria"""
        operand_type = self.visit_Expression(node.operand)

        if node.operator.type == TokenType.OP_NOT:
            if not self.type_system.is_compatible_for_op(operand_type, operand_type, "unary_logical"):
                self.errors.append(
                    f"[L{node.operator.line},C{node.operator.column}] "
                    f"Cannot apply ! to {operand_type}"
                )
            return TypeKind.BOOL

        elif node.operator.type in [TokenType.OP_RESTA, TokenType.OP_INC, TokenType.OP_DEC]:
            if not self.type_system.is_compatible_for_op(operand_type, operand_type, "unary_arithmetic"):
                self.errors.append(
                    f"[L{node.operator.line},C{node.operator.column}] "
                    f"Cannot apply {node.operator.lexeme} to {operand_type}"
                )
            return operand_type

        return operand_type

    def visit_CallExpr(self, node: CallExpr) -> TypeKind:
        """Analiza llamada a función"""
        func_name = node.func_token.lexeme
        func_sym = self.current_scope.lookup(func_name)

        if func_sym is None:
            self.errors.append(
                f"[L{node.func_token.line},C{node.func_token.column}] "
                f"Undefined function '{func_name}'"
            )
            return TypeKind.ERROR

        if func_sym.kind != "function":
            self.errors.append(
                f"[L{node.func_token.line},C{node.func_token.column}] "
                f"'{func_name}' is not a function"
            )
            return TypeKind.ERROR

        # Verificar argumentos
        if len(node.arguments) != len(func_sym.param_types or []):
            self.errors.append(
                f"[L{node.func_token.line},C{node.func_token.column}] "
                f"Function '{func_name}' expects {len(func_sym.param_types or [])} "
                f"arguments, got {len(node.arguments)}"
            )

        for i, arg in enumerate(node.arguments):
            arg_type = self.visit_Expression(arg)
            if i < len(func_sym.param_types or []):
                expected_type = func_sym.param_types[i]
                if not self.type_system.is_assignable(expected_type, arg_type):
                    self.errors.append(
                        f"[L{node.func_token.line},C{node.func_token.column}] "
                        f"Argument {i} type mismatch: expected {expected_type}, got {arg_type}"
                    )

        return func_sym.return_type or TypeKind.ERROR

    def visit_IndexExpr(self, node: IndexExpr) -> TypeKind:
        """Analiza acceso a arreglo"""
        array_name = node.array_token.lexeme
        array_sym = self.current_scope.lookup(array_name)

        if array_sym is None:
            self.errors.append(
                f"[L{node.array_token.line},C{node.array_token.column}] "
                f"Undefined variable '{array_name}'"
            )
            return TypeKind.ERROR

        index_type = self.visit_Expression(node.index)
        if not self.type_system.is_numeric(index_type):
            self.errors.append(
                f"[L{node.array_token.line}] "
                f"Array index must be numeric, got {index_type}"
            )

        return array_sym.type_

    def visit_LiteralExpr(self, node: LiteralExpr) -> TypeKind:
        """Analiza literal"""
        return self.type_system.get_literal_type(node.value_token)

    def visit_IdentifierExpr(self, node: IdentifierExpr) -> TypeKind:
        """Analiza identificador (variable)"""
        var_name = node.id_token.lexeme
        var_sym = self.current_scope.lookup(var_name)

        if var_sym is None:
            self.errors.append(
                f"[L{node.id_token.line},C{node.id_token.column}] "
                f"Undefined variable '{var_name}'"
            )
            return TypeKind.ERROR

        return var_sym.type_

    def visit_GroupingExpr(self, node: GroupingExpr) -> TypeKind:
        """Analiza expresión agrupada"""
        return self.visit_Expression(node.expression)

    # ===== Utilidades =====

    def _get_node_line(self, node: Expression) -> int:
        """Extrae la línea de un nodo de expresión"""
        if isinstance(node, LiteralExpr):
            return node.value_token.line
        elif isinstance(node, IdentifierExpr):
            return node.id_token.line
        elif isinstance(node, CallExpr):
            return node.func_token.line
        elif isinstance(node, IndexExpr):
            return node.array_token.line
        elif isinstance(node, BinaryExpr):
            return node.operator.line
        elif isinstance(node, UnaryExpr):
            return node.operator.line
        elif isinstance(node, AssignExpr):
            return node.target_token.line
        elif isinstance(node, GroupingExpr):
            return self._get_node_line(node.expression)
        return 0

    def token_to_type(self, token: Token) -> TypeKind:
        """Convierte un token de tipo a TypeKind"""
        type_map = {
            TokenType.INT: TypeKind.INT,
            TokenType.FLOAT: TypeKind.FLOAT,
            TokenType.DOUBLE: TypeKind.DOUBLE,
            TokenType.CHAR: TypeKind.CHAR,
            TokenType.BOOL: TypeKind.BOOL,
            TokenType.VOID: TypeKind.VOID,
        }
        return type_map.get(token.type, TypeKind.ERROR)
