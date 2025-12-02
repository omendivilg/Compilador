# FIRST y FOLLOW – Gramática Actualizada

Este documento resume los conjuntos **FIRST** y **FOLLOW** para la gramática completa del compilador.

---

## FIRST (qué puede iniciar cada regla)

### FIRST(S)

{ bof }

scss
Copy code

### FIRST(PROGRAMA), LISTADECL, DECL

{ int, float, double, char, bool, void, class }

scss
Copy code
Representan cualquier tipo de declaración inicial.

### FIRST(TIPO)

{ int, float, double, char, bool, void }

scss
Copy code

### FIRST(DECLVAR), FIRST(DECLVARSINPUNTO)

Ambas comienzan con un tipo:
{ int, float, double, char, bool, void }

scss
Copy code

### FIRST(LISTAID)

{ id }

scss
Copy code

### FIRST(INICIALIZACION)

{ op_asig, ε }

scss
Copy code

### FIRST(DECLFUNC)

{ int, float, double, char, bool, void }

scss
Copy code

### FIRST(DECLCLASE)

{ class }

scss
Copy code

### FIRST(MIEMBRO)

{ public, private, int, float, double, char, bool, void }

scss
Copy code

### FIRST(BLOQUE)

{ llave_izq }

scss
Copy code

### FIRST(SENTENCIA)

Incluye todos los elementos que pueden iniciar una sentencia:
{
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec, punto_coma,
if, while, for, return, switch, llave_izq
}

scss
Copy code

### FIRST(SENTENCIASEL)

{ if }

scss
Copy code

### FIRST(SENTENCIAITER)

{ while, for }

scss
Copy code

### FIRST(SENTENCIARET)

{ return }

scss
Copy code

### FIRST(SENTENCIASWITCH)

{ switch }

scss
Copy code

### FIRST(FORINIT)

{
int, float, double, char, bool, void,
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec,
ε
}

scss
Copy code

### FIRST(FORUPDATE)

FIRST(EXPR) ∪ { ε }

scss
Copy code

### FIRST(CASO), FIRST(LISTACASOS)

{ case, default }

scss
Copy code

### FIRST(EXPR) (y todos sus niveles)

{
id, num_int, num_float, num_exp, string, char,
true, false,
paren_izq,
op_not, op_resta, op_inc, op_dec
}

yaml
Copy code

---

## FOLLOW (qué puede venir después de cada regla)

### FOLLOW(S), FOLLOW(PROGRAMA), FOLLOW(LISTADECL)

{ eof }

scss
Copy code

### FOLLOW(DECL)

{ int, float, double, char, bool, void, class, eof }

scss
Copy code

### FOLLOW(LISTAID), FOLLOW(DECLVARSINPUNTO)

{ punto_coma }

scss
Copy code

### FOLLOW(TIPO)

{ id }

scss
Copy code

### FOLLOW(BLOQUE)

{
else, while, for, if, return, switch,
llave_der, case, default, eof,
int, float, double, char, bool, void, class
}

scss
Copy code

### FOLLOW(SENTENCIA), FOLLOW(LISTASENTENCIAS)

{ llave_der }

scss
Copy code

### FOLLOW(SENTENCIASWITCH)

{ llave_der }

scss
Copy code

### FOLLOW(LISTACASOS)

{ llave_der }

scss
Copy code

### FOLLOW(CASO)

{ case, default, llave_der }

yaml
Copy code

---

## FOLLOW(EXPR) – para todos los niveles de expresiones

Cualquier expresión puede ser seguida por operadores o delimitadores:

{
op_asig,
op_or,
op_and,
op_igual, op_distinto,
op_menor, op_menor_ig, op_mayor, op_mayor_ig,
op_suma, op_resta,
op_mult, op_div, op_mod,
op_inc, op_dec,
paren_der,
corchete_der,
coma,
punto_coma
}
