# Gramática de Producción - Analizador Léxico

## Reglas de Producción en Formato Árbol

S → bof PROGRAMA eof

PROGRAMA → LISTADECL

LISTADECL → DECL LISTADECL’
LISTADECL’ → DECL LISTADECL’ | ε

DECL → DECLVAR | DECLFUNC | DECLCLASE

DECLVAR → TIPO LISTAID punto_coma
DECLVARSINPUNTO → TIPO LISTAID

LISTAID → id INICIALIZACION LISTAID’
LISTAID’ → coma id INICIALIZACION LISTAID’ | ε

INICIALIZACION → op_asig EXPR | ε

TIPO → int | float | double | char | bool | void

DECLFUNC → TIPO id paren_izq PARAMETROS paren_der BLOQUE
| TIPO id paren_izq paren_der BLOQUE

PARAMETROS → PARAMLISTA | ε

PARAMLISTA → PARAM PARAMLISTA’
PARAMLISTA’ → coma PARAM PARAMLISTA’ | ε

PARAM → TIPO id

DECLCLASE → class id llave_izq LISTAMIEMBROS llave_der

LISTAMIEMBROS → MIEMBRO LISTAMIEMBROS’
LISTAMIEMBROS’ → MIEMBRO LISTAMIEMBROS’ | ε

MIEMBRO → MODIFICADORACCESO DECLVAR
| MODIFICADORACCESO DECLFUNC

MODIFICADORACCESO → public | private | ε

BLOQUE → llave_izq LISTASENTENCIAS llave_der

LISTASENTENCIAS → SENTENCIA LISTASENTENCIAS’
LISTASENTENCIAS’ → SENTENCIA LISTASENTENCIAS’ | ε

SENTENCIA → SENTENCIAEXPR
| SENTENCIASEL
| SENTENCIAITER
| SENTENCIARET
| SENTENCIASWITCH
| BLOQUE

SENTENCIAEXPR → EXPR punto_coma
| punto_coma

SENTENCIASEL → if paren_izq EXPR paren_der SENTENCIA
| if paren_izq EXPR paren_der SENTENCIA else SENTENCIA

SENTENCIAITER → while paren_izq EXPR paren_der SENTENCIA
| for paren_izq FORINIT punto_coma EXPR punto_coma FORUPDATE paren_der SENTENCIA

FORINIT → DECLVARSINPUNTO
| EXPR
| ε

FORUPDATE → EXPR
| ε

SENTENCIARET → return EXPR punto_coma
| return punto_coma

SENTENCIASWITCH → switch paren_izq EXPR paren_der llave_izq LISTACASOS llave_der

LISTACASOS → CASO LISTACASOS’
LISTACASOS’ → CASO LISTACASOS’ | ε

CASO → case EXPR punto_coma LISTASENTENCIAS
| default punto_coma LISTASENTENCIAS

EXPR → EXPRASIGNACION

EXPRASIGNACION → EXPRLOGICA EXPRASIGNACION’
EXPRASIGNACION’ → op_asig EXPRASIGNACION | ε

EXPRLOGICA → EXPRAND EXPRLOGICA’
EXPRLOGICA’ → op_or EXPRAND EXPRLOGICA’ | ε

EXPRAND → EXPRIGUALDAD EXPRAND’
EXPRAND’ → op_and EXPRIGUALDAD EXPRAND’ | ε

EXPRIGUALDAD → EXPRRELACIONAL EXPRIGUALDAD’
EXPRIGUALDAD’ → op_igual EXPRRELACIONAL EXPRIGUALDAD’
| op_distinto EXPRRELACIONAL EXPRIGUALDAD’
| ε

EXPRRELACIONAL → EXPRADITIVA EXPRRELACIONAL’
EXPRRELACIONAL’ → op_menor EXPRADITIVA EXPRRELACIONAL’
| op_menor_ig EXPRADITIVA EXPRRELACIONAL’
| op_mayor EXPRADITIVA EXPRRELACIONAL’
| op_mayor_ig EXPRADITIVA EXPRRELACIONAL’
| ε

EXPRADITIVA → TERM EXPRADITIVA’
EXPRADITIVA’ → op_suma TERM EXPRADITIVA’
| op_resta TERM EXPRADITIVA’
| ε

TERM → FACTOR TERM’
TERM’ → op_mult FACTOR TERM’
| op_div FACTOR TERM’
| op_mod FACTOR TERM’
| ε

FACTOR → op_not FACTOR
| op_resta FACTOR
| op_inc EXPRPOSTFIJA
| op_dec EXPRPOSTFIJA
| EXPRPOSTFIJA

EXPRPOSTFIJA → EXPRPRIMARIA EXPRPOSTFIJA’
EXPRPOSTFIJA’ → op_inc
| op_dec
| ε

EXPRPRIMARIA → id
| LITERAL
| paren_izq EXPR paren_der
| LLAMADAFUNC
| ACCESOARREGLO

LLAMADAFUNC → id paren_izq ARGSOPTS paren_der
ARGSOPTS → LISTAARGS | ε

LISTAARGS → EXPR LISTAARGS’
LISTAARGS’ → coma EXPR LISTAARGS’
| ε

ACCESOARREGLO → id corchete_izq EXPR corchete_der

LITERAL → num_int
| num_float
| num_exp
| string
| char
| true
| false

## Palabras Reservadas:

int, float, double, char, bool, void
if, else, while, for, switch, case, default
return, class, public, private
true, false

## Operadores:

Aritméticos:
op_suma (+)
op_resta (-)
op_mult (\*)
op_div (/)
op_mod (%)
Asignación:
op_asig (=)

## Incremento / Decremento:

op_inc (++)
op_dec (--)
Relacionales:
op_menor (<)
op_menor_ig (<=)
op_mayor (>)
op_mayor_ig (>=)
Igualdad:
op_igual (==)
op_distinto (!=)
Lógicos:
op_and (&&)
op_or (||)
op_not (!)

## Delimitadores:

paren_izq ( ( )
paren_der ( ) )
llave_izq ( { )
llave_der ( } )
corchete_izq ( [ )
corchete_der ( ] )
punto_coma ( ; )
coma ( , )
punto ( . ) (si lo usas para notación de objetos, opcional)

## Literales y Identificadores:

id — identificadores
num_int, num_float, num_exp — números
string, char — cadenas y caracteres

Especiales:
bof — beginning of file
eof — end of file
ε — cadena vacía (solo en gramática, no token real)

## Precedencia de Operadores (Mayor a Menor)

() , []
paréntesis, acceso a arreglos
expr++, expr--
postfijo
++expr, --expr, !expr, -expr
prefijo / unario
\*, /, %
+, -
<, <=, >, >=
==, !=
&&
||
= (asignación)

## Asociatividad

## Izquierda a derecha:

+, -, \*, /, %
<, <=, >, >=
==, !=
&&
||
llamadas | indexado | secuencias

## Derecha a izquierda:

=

operadores unarios: ++, --, !, - (unario)
