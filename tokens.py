# tokens.py
from enum import Enum, auto


class TokenType(Enum):
    # ---- control del archivo ----
    BOF = auto()
    EOF = auto()

    # ---- tipos ----
    INT = auto()
    FLOAT = auto()
    DOUBLE = auto()
    CHAR = auto()
    BOOL = auto()
    VOID = auto()

    # ---- palabras reservadas ----
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    RETURN = auto()

    CLASS = auto()
    PUBLIC = auto()
    PRIVATE = auto()

    TRUE = auto()
    FALSE = auto()

    # ---- operadores aritméticos ----
    OP_SUMA = auto()      # +
    OP_RESTA = auto()     # -
    OP_MULT = auto()      # *
    OP_DIV = auto()       # /
    OP_MOD = auto()       # %

    # ---- operadores unarios ----
    OP_INC = auto()       # ++
    OP_DEC = auto()       # --

    # ---- operadores relacionales ----
    OP_MENOR = auto()        # <
    OP_MENOR_IG = auto()     # <=
    OP_MAYOR = auto()        # >
    OP_MAYOR_IG = auto()     # >=
    OP_IGUAL = auto()        # ==
    OP_DISTINTO = auto()     # !=

    # ---- operadores lógicos ----
    OP_AND = auto()      # &&
    OP_OR = auto()       # ||
    OP_NOT = auto()      # !

    # ---- asignación ----
    OP_ASIG = auto()     # =

    # ---- símbolos ----
    PAREN_IZQ = auto()      # (
    PAREN_DER = auto()      # )
    LLAVE_IZQ = auto()      # {
    LLAVE_DER = auto()      # }
    CORCHETE_IZQ = auto()   # [
    CORCHETE_DER = auto()   # ]

    PUNTO_COMA = auto()     # ;
    COMA = auto()           # ,
    PUNTO = auto()          # .

    # ---- comentarios ----
    COMMENT_LINE = auto()    # //
    COMMENT_BLOCK = auto()   # /* ... */

    # ---- identificadores y literales ----
    ID = auto()
    NUM_INT = auto()
    NUM_FLOAT = auto()
    STRING = auto()         # "cadena"
    CHAR_LITERAL = auto()   # 'a'

    # ---- error ----
    ERROR = auto()


class Token:
    def __init__(self, type_, lexeme, line, column=0):
        self.type = type_
        self.lexeme = lexeme
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, line={self.line}, col={self.column})"
