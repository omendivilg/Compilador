from analizador_lexico import Lexer, LexError
from parser import Parser, ParserError


def main():
    # 1. Leer el archivo de prueba
    with open("test.txt", "r", encoding="utf-8") as f:
        code = f.read()

    # 2. ANÁLISIS LÉXICO
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

    # 3. ANÁLISIS SINTÁCTICO
    print("\n=== PARSEANDO ===")
    try:
        parser = Parser(tokens)
        parser.parse()
        print("✅ Sintaxis válida")
    except ParserError as e:
        print("❌ Error de sintaxis:")
        print(e)


if __name__ == "__main__":
    main()
