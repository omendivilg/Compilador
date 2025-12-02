from analizador_lexico import Lexer, LexError
from parser import Parser, ParserError
from analizador_semantico import SemanticAnalyzer
import sys

# Configurar encoding para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def main():
    # 1. Leer el archivo de prueba
    FILENAME = "test_ok.txt"
    print("[DEBUG] Iniciando compilador...")
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            code = f.read()
        print(f"[DEBUG] Archivo {FILENAME} leído ({len(code)} caracteres)")
    except FileNotFoundError:
        print(f" Error: No se encontró {FILENAME}")
        return
    except Exception as e:
        print(f" Error al leer archivo: {e}")
        return

    # ===== FASE 1: ANÁLISIS LÉXICO =====
    print("\n[DEBUG] Iniciando análisis léxico...")
    try:
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        print(f"[DEBUG] Análisis léxico completado ({len(tokens)} tokens generados)")
    except LexError as e:
        print("❌ Error lexico:")
        print(e)
        return
    except Exception as e:
        print(f"❌ Error inesperado en análisis léxico: {e}")
        return

    print("=== TOKENS ===")
    for t in tokens:
        print(t)

    # ===== FASE 2: ANÁLISIS SINTÁCTICO (Genera AST) =====
    print("\n=== ANALISIS SINTACTICO ===")
    print("[DEBUG] Iniciando análisis sintáctico...")
    try:
        parser = Parser(tokens)
        print("[DEBUG] Parser inicializado, comenzando parse()...")
        ast = parser.parse()  # Retorna el AST (Program node)
        print(f"[DEBUG] Análisis sintáctico completado, AST generado")
        print("✅ Sintaxis valida")
    except ParserError as e:
        print("❌ Error de sintaxis:")
        print(e)
        return
    except Exception as e:
        print(f"❌ Error inesperado en análisis sintáctico: {e}")
        import traceback
        traceback.print_exc()
        return

    # ===== FASE 3: ANÁLISIS SEMÁNTICO =====
    print("\n=== ANALISIS SEMANTICO ===")
    print("[DEBUG] Iniciando análisis semántico...")
    try:
        analyzer = SemanticAnalyzer()
        print("[DEBUG] SemanticAnalyzer inicializado")
        semantic_errors = analyzer.analyze(ast)
        print(f"[DEBUG] Análisis semántico completado ({len(semantic_errors)} errores encontrados)")
    except Exception as e:
        print(f"❌ Error inesperado en análisis semántico: {e}")
        import traceback
        traceback.print_exc()
        return

    if semantic_errors:
        print("❌ Errores semanticos encontrados:")
        for error in semantic_errors:
            print(f"  • {error}")
    else:
        print(" Analisis semantico valido")
        print("\n" + "="*50)
        print(" COMPILACION EXITOSA")
        print("="*50)


if __name__ == "__main__":
    main()
