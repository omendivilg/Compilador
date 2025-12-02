# FIRST Rules

FIRST(S) = { bof }

FIRST(PROGRAMA) = { int, float, double, char, bool, void, class }
FIRST(LISTADECL) = { int, float, double, char, bool, void, class }
FIRST(LISTADECL') = { int, float, double, char, bool, void, class, ε }

FIRST(DECL) = { int, float, double, char, bool, void, class }

FIRST(DECLVAR) = { int, float, double, char, bool, void }
FIRST(DECLVARSINPUNTO) = { int, float, double, char, bool, void }

FIRST(LISTAID) = { id }
FIRST(LISTAID') = { coma, ε }

FIRST(INICIALIZACION) = { op_asig, ε }

FIRST(TIPO) = { int, float, double, char, bool, void }

FIRST(DECLFUNC) = { int, float, double, char, bool, void }

FIRST(PARAMETROS) = { int, float, double, char, bool, void, ε }
FIRST(PARAMLISTA) = { int, float, double, char, bool, void }
FIRST(PARAMLISTA') = { coma, ε }
FIRST(PARAM) = { int, float, double, char, bool, void }

FIRST(DECLCLASE) = { class }
FIRST(LISTAMIEMBROS) = { public, private, int, float, double, char, bool, void, ε }
FIRST(LISTAMIEMBROS') = { public, private, int, float, double, char, bool, void, ε }
FIRST(MIEMBRO) = { public, private, int, float, double, char, bool, void }

FIRST(MODIFICADORACCESO) = { public, private, ε }

FIRST(BLOQUE) = { llave_izq }
FIRST(LISTASENTENCIAS) = {
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec, punto_coma,
if, while, for, return, switch, llave_izq,
ε
}
FIRST(LISTASENTENCIAS') = {
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec, punto_coma,
if, while, for, return, switch, llave_izq,
ε
}

FIRST(SENTENCIA) = {
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec, punto_coma,
if, while, for, return, switch, llave_izq
}

FIRST(SENTENCIAEXPR) = {
id, num_int, num_float, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec, punto_coma
}

FIRST(SENTENCIASEL) = { if }
FIRST(SENTENCIAITER) = { while, for }
FIRST(SENTENCIARET) = { return }
FIRST(SENTENCIASWITCH) = { switch }

FIRST(FORINIT) = {
int, float, double, char, bool, void,
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec,
ε
}

FIRST(FORUPDATE) = {
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec,
ε
}

FIRST(LISTACASOS) = { case, default }
FIRST(LISTACASOS') = { case, default, ε }
FIRST(CASO) = { case, default }

FIRST(EXPR) = {
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq, op_not, op_resta, op_inc, op_dec
}

FIRST(EXPRASIGNACION) = FIRST(EXPR)
FIRST(EXPRASIGNACION') = { op_asig, ε }

FIRST(EXPRLOGICA) = FIRST(EXPR)
FIRST(EXPRLOGICA') = { op_or, ε }

FIRST(EXPRAND) = FIRST(EXPR)
FIRST(EXPRAND') = { op_and, ε }

FIRST(EXPRIGUALDAD) = FIRST(EXPR)
FIRST(EXPRIGUALDAD') = { op_igual, op_distinto, ε }

FIRST(EXPRRELACIONAL) = FIRST(EXPR)
FIRST(EXPRRELACIONAL') = { op_menor, op_menor_ig, op_mayor, op_mayor_ig, ε }

FIRST(EXPRADITIVA) = FIRST(EXPR)
FIRST(EXPRADITIVA') = { op_suma, op_resta, ε }

FIRST(TERM) = FIRST(EXPR)
FIRST(TERM') = { op_mult, op_div, op_mod, ε }

FIRST(FACTOR) = {
op_not, op_resta, op_inc, op_dec,
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq
}

FIRST(EXPRPOSTFIJA) = FIRST(EXPRPRIMARIA)
FIRST(EXPRPOSTFIJA') = { op_inc, op_dec, ε }

FIRST(EXPRPRIMARIA) = {
id, num_int, num_float, num_exp, string, char, true, false,
paren_izq
}

FIRST(LLAMADAFUNC) = { id }
FIRST(ARGSOPTS) = { id, num_int, num_float, num_exp, string, char, true, false, paren_izq, op_not, op_resta, op_inc, op_dec, ε }
FIRST(LISTAARGS) = FIRST(EXPR)
FIRST(LISTAARGS') = { coma, ε }

FIRST(ACCESOARREGLO) = { id }

FIRST(LITERAL) = { num_int, num_float, num_exp, string, char, true, false }

---

# FOLLOW Rules

FOLLOW(S) = { eof }
FOLLOW(PROGRAMA) = { eof }
FOLLOW(LISTADECL) = { eof }

FOLLOW(DECL) = { int, float, double, char, bool, void, class, eof }

FOLLOW(LISTAID') = { punto_coma }

FOLLOW(TIPO) = { id }

FOLLOW(PARAMETROS) = { paren_der }
FOLLOW(PARAMLISTA) = { paren_der }
FOLLOW(PARAMLISTA') = { paren_der }
FOLLOW(PARAM) = { coma, paren_der }

FOLLOW(DECLCLASE) = { int, float, double, char, bool, void, class, eof }

FOLLOW(BLOQUE) = {
int, float, double, char, bool, void,
id, lparen, num_int, num_float, num_exp, string, char, true, false,
op_not, punto_coma, if, else, while, for, return, switch,
llave_izq, llave_der, eof
}

FOLLOW(LISTASENTENCIAS) = { llave_der }
FOLLOW(SENTENCIA) = {
int, float, double, char, bool, void,
id, paren_izq, num_int, num_float, num_exp, string, char, true, false,
op_not, punto_coma, if, else, while, for, return, switch,
llave_izq, llave_der
}

FOLLOW(SENTENCIASEL) = FOLLOW(SENTENCIA)
FOLLOW(SENTENCIAITER) = FOLLOW(SENTENCIA)
FOLLOW(SENTENCIARET) = FOLLOW(SENTENCIA)
FOLLOW(SENTENCIASWITCH) = FOLLOW(SENTENCIA)

FOLLOW(CASO) = { case, default, llave_der }

FOLLOW(EXPR) = {
punto_coma, paren_der, coma, corchete_der,
op_asig,
op_or, op_and,
op_igual, op_distinto,
op_menor, op_menor_ig, op_mayor, op_mayor_ig,
op_suma, op_resta,
op_mult, op_div, op_mod,
op_inc, op_dec
}

FOLLOW(EXPRASIGNACION) = FOLLOW(EXPR)
FOLLOW(EXPRLOGICA) = FOLLOW(EXPR)
FOLLOW(EXPRAND) = FOLLOW(EXPR)
FOLLOW(EXPRIGUALDAD) = FOLLOW(EXPR)
FOLLOW(EXPRRELACIONAL) = FOLLOW(EXPR)
FOLLOW(EXPRADITIVA) = FOLLOW(EXPR)
FOLLOW(TERM) = FOLLOW(EXPR)
FOLLOW(FACTOR) = FOLLOW(EXPR)
FOLLOW(EXPRPOSTFIJA) = FOLLOW(EXPR)
FOLLOW(EXPRPRIMARIA) = FOLLOW(EXPR)
FOLLOW(LLAMADAFUNC) = FOLLOW(EXPR)
FOLLOW(ACCESOARREGLO) = FOLLOW(EXPR)
FOLLOW(LISTAARGS) = { paren_der }
FOLLOW(LISTAARGS') = { paren_der }
