# Gramática de Producción - Analizador Léxico

## Reglas de Producción en Formato Árbol

S → bof PROGRAMA eof

PROGRAMA → LISTADECL

LISTADECL → DECL LISTADECL | ε

DECL → DECLVAR | DECLFUNC | DECLCLASE

DECLVAR → TIPO LISTAID punto_coma

LISTAID → id INICIALIZACION | id INICIALIZACION coma LISTAID

INICIALIZACION → op_asig EXPR | ε

TIPO → int | float | double | char | bool | void

DECLFUNC → TIPO id paren_izq PARAMETROS paren_der BLOQUE | TIPO id paren_izq paren_der BLOQUE

PARAMETROS → PARAMLISTA | ε

PARAMLISTA → PARAM | PARAM coma PARAMLISTA

PARAM → TIPO id

DECLCLASE → class id llave_izq LISTAMIEMBROS llave_der

LISTAMIEMBROS → MIEMBRO LISTAMIEMBROS | ε

MIEMBRO → MODIFICADORACCESO DECLVAR | MODIFICADORACCESO DECLFUNC

MODIFICADORACCESO → public | private | ε

BLOQUE → llave_izq LISTASENTENCIAS llave_der

LISTASENTENCIAS → SENTENCIA LISTASENTENCIAS | ε

SENTENCIA → SENTENCIAEXPR | SENTENCIASEL | SENTENCIAITER | SENTENCIARET | SENTENCIASWITCH | BLOQUE

SENTENCIAEXPR → EXPR punto_coma | punto_coma

SENTENCIASEL → if paren_izq EXPR paren_der SENTENCIA | if paren_izq EXPR paren_der SENTENCIA else SENTENCIA

SENTENCIAITER → while paren_izq EXPR paren_der SENTENCIA | for paren_izq FORINIT punto_coma EXPR punto_coma FORUPDATE paren_der SENTENCIA

FORINIT → DECLVARSINPUNTO | EXPR | ε

FORUPDATE → EXPR | ε

DECLVARSINPUNTO → TIPO LISTAID

SENTENCIARET → return EXPR punto_coma | return punto_coma

SENTENCIASWITCH → switch paren_izq EXPR paren_der llave_izq LISTACASOS llave_der

LISTACASOS → CASO LISTACASOS | ε

CASO → case EXPR punto_coma LISTASENTENCIAS | default punto_coma LISTASENTENCIAS

EXPR → EXPRASIGNACION

EXPRASIGNACION → id op_asig EXPR | EXPRLOGICA

EXPRLOGICA → EXPRLOGICA op_or EXPRAND | EXPRAND

EXPRAND → EXPRAND op_and EXPRIGUALDAD | EXPRIGUALDAD

EXPRIGUALDAD → EXPRIGUALDAD op_igual EXPRRELACIONAL | EXPRIGUALDAD op_distinto EXPRRELACIONAL | EXPRRELACIONAL

EXPRRELACIONAL → EXPRRELACIONAL op_menor EXPRADITIVA | EXPRRELACIONAL op_menor_ig EXPRADITIVA | EXPRRELACIONAL op_mayor EXPRADITIVA | EXPRRELACIONAL op_mayor_ig EXPRADITIVA | EXPRADITIVA

EXPRADITIVA → EXPRADITIVA op_suma TERM | EXPRADITIVA op_resta TERM | TERM

TERM → TERM op_mult FACTOR | TERM op_div FACTOR | TERM op_mod FACTOR | FACTOR

FACTOR → op_not FACTOR | op_resta FACTOR | op_inc EXPRPOSTFIJA | op_dec EXPRPOSTFIJA | EXPRPOSTFIJA

EXPRPOSTFIJA → EXPRPRIMARIA op_inc | EXPRPRIMARIA op_dec | EXPRPRIMARIA

EXPRPRIMARIA → id | LITERAL | paren_izq EXPR paren_der | LLAMADAFUNC | ACCESOARREGLO

LLAMADAFUNC → id paren_izq LISTAARGS paren_der | id paren_izq paren_der

LISTAARGS → EXPR | EXPR coma LISTAARGS

ACCESOARREGLO → id corchete_izq EXPR corchete_der

LITERAL → num_int | num_float | num_exp | string | char | true | false

ID → id
ε → ε

## Tokens Terminales Utilizados

### Palabras Reservadas:

- int, float, double, char, bool, void
- if, else, while, for, switch, case, default
- return, class, public, private
- true, false

### Operadores:

- Aritméticos: op_suma, op_resta, op_mult, op_div, op_mod
- Asignación: op_asig
- Incremento/Decremento: op_inc, op_dec
- Relacionales: op_menor, op_menor_ig, op_mayor, op_mayor_ig
- Igualdad: op_igual, op_distinto
- Lógicos: op_and, op_or, op_not

### Delimitadores:

- paren_izq, paren_der
- llave_izq, llave_der
- corchete_izq, corchete_der
- punto_coma, coma, punto

### Literales y Identificadores:

- id (identificadores)
- num_int, num_float, num_exp (números)
- string, char (cadenas y caracteres)

### Especiales:

- bof (beginning of file)
- eof (end of file)
- ε (épsilon - cadena vacía)

## Precedencia de Operadores (Mayor a Menor):

1. (), [] - paréntesis, acceso a arreglos
2. ++, -- (postfijo)
3. ++, -- (prefijo), !, - (unario)
4. \*, /, %
5. +, -
6. <, <=, >, >=
7. ==, !=
8. &&
9. ||
10. = (asignación)

## Asociatividad:

- Izquierda a derecha: operadores aritméticos, relacionales, lógicos
- Derecha a izquierda: asignación, operadores unarios
