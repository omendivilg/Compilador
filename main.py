from analizador_lexico import Lexer, LexError
from parser import Parser, ParserError
from analizador_semantico import SemanticAnalyzer


def main():
    # 1. Leer el archivo de prueba
    with open("test.txt", "r", encoding="utf-8") as f:
        code = f.read()

    # ===== FASE 1: ANÁLISIS LÉXICO =====
    try:
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
    except LexError as e:
        print("❌ Error léxico:")
        print(e)
        return

    print("=== TOKENS ===")
    for t in tokens:
        print(t)

    # ===== FASE 2: ANÁLISIS SINTÁCTICO (Genera AST) =====
    print("\n=== ANÁLISIS SINTÁCTICO ===")
    try:
        parser = Parser(tokens)
        ast = parser.parse()  # Retorna el AST (Program node)
        print("✅ Sintaxis válida")
    except ParserError as e:
        print("❌ Error de sintaxis:")
        print(e)
        return

    # ===== FASE 3: ANÁLISIS SEMÁNTICO =====
    print("\n=== ANÁLISIS SEMÁNTICO ===")
    analyzer = SemanticAnalyzer()
    semantic_errors = analyzer.analyze(ast)

    if semantic_errors:
        print("❌ Errores semánticos encontrados:")
        for error in semantic_errors:
            print(f"  • {error}")
    else:
        print("✅ Análisis semántico válido")
        print("\n" + "="*50)
        print("✅ COMPILACIÓN EXITOSA")
        print("="*50)


if __name__ == "__main__":
    main()
