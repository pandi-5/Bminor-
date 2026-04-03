import sys 
import argparse
from parser import Parser
from lexer_mio import Lexer
from checker import Checker

def compilar(filename):
    try:
        txt = open(filename, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{filename}'.")
        return

    p = Parser()
    l = Lexer()
    p.code = txt
    ast = p.parse(l.tokenize(txt))

    if ast is None:
        print("Error: El código tiene errores de sintaxis. No se pudo generar el AST.")
        return

    # --- PASO 3: CHECKER (Análisis Semántico) ---
    checker = Checker()
    checker.visit(ast)

    # --- PASO 4: REPORTE DE RESULTADOS ---
    if len(checker.errors) > 0:
        print("SE ENCONTRARON ERRORES SEMÁNTICOS")
        print("-" * 40)
        for error in checker.errors:
            print(error)
        print("-" * 40)
    else:
        print("Compilación exitosa. ¡El código es semánticamente correcto!")


if __name__ == '__main__':
    terminal = argparse.ArgumentParser(description='Compilador para B++')
    terminal.add_argument('filename', help='Archivo prueba a compilar')
    args = terminal.parse_args()

    if not args.filename:
        print("Error: No se proporcionó un archivo para compilar.")
        sys.exit(1)

    compilar(args.filename)