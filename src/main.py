import os
import argparse
from parser import Parser
from lexer_mio import Lexer
from checker import Checker
from visualizer import build_rich_tree, build_graphviz
from rich import print as rprint
from graphviz import Digraph
import errors

def compilar(fase, filename, use_rich=False, use_graphviz=False):
    try:
        txt = open(filename, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{filename}'.")
        return

    # 1. Analisis Léxico (Ejecuta el lexer y muestra los tokens)
    l = Lexer()
    
    if fase == 'lexer':
        print("--- INICIANDO ANÁLISIS LÉXICO ---")
        for tok in l.tokenize(txt):
            rprint(tok)
        print("--- ANÁLISIS LÉXICO TERMINADO ---")
        return

    # 2. Analisis Sintáctico (Ejecuta el parser y muestra el AST)
    p = Parser()
    p.code = txt
    ast = p.parse(l.tokenize(txt))

    if ast is None or errors.errors_detected() > 0:
        print("Error: Se encontraron errores de sintaxis. No se pudo generar el AST.")
        print(f"Total de errores de sintaxis: {errors.errors_detected()}")
        return

    if fase == 'parser':
        print("--- INICIANDO ANÁLISIS SINTÁCTICO ---")
        print("AST generado exitosamente. No se encontraron errores de sintaxis.")
        
        # evaluamos si se uso la bandera --rich
        if use_rich:
            print("Visualización de AST por consola usando Rich:")
            print("ÁRBOL EN CONSOLA\n")
            arbol_rich = build_rich_tree(ast)
            rprint(arbol_rich)
            
        # evaluamos si se uso la bandera --graphviz
        if use_graphviz:
            print("Visualización de AST exportada a un diagrama de Graphviz.")
            print("GENERANDO IMAGEN")
            dot = Digraph(comment='AST B-Minor')
            build_graphviz(ast, dot)
            
            nombre_base = os.path.basename(filename)
            nombre_sin_ext = os.path.splitext(nombre_base)[0]
            nombre_archivo = f"ast_{nombre_sin_ext}"
            os.makedirs(os.path.join("images"), exist_ok=True)
            ruta_salida = os.path.join("images", nombre_archivo)
            dot.render(ruta_salida, format="png", cleanup=True)
            print(f"Imagen generada en: {ruta_salida}.png\n")
            
        return

    # 3. Análisis Semántico (Ejecuta el checker para validar el AST)
    if fase == 'checker':
        print("--- INICIANDO ANÁLISIS SEMÁNTICO ---")
        checker = Checker()
        checker.visit(ast)
    
        if len(checker.errors) > 0:
            print("SE ENCONTRARON ERRORES SEMÁNTICOS")
            print("-" * 40)
            for error in checker.errors:
                print(error)
            print("-" * 40)
        else:
            print("Compilacion exitosa. No se encontraron errores semánticos.")
        return


if __name__ == '__main__':
    terminal = argparse.ArgumentParser(description='Compilador para B++')
    
    # argumento para elegir la fase del compilador donde se desea detener la ejecución
    terminal.add_argument(
        'fase', 
        choices=['lexer', 'parser', 'checker'], 
        help='Fase del compilador donde deseas detenerte'
    )

    # argumento para el archivo de prueba a compilar   
    terminal.add_argument('filename', help='Archivo de prueba a compilar')
    
    # argumentos opcionales para visualización del AST en consola con Rich o exportación a imagen con Graphviz
    # solo aplican para la fase parser
    terminal.add_argument(
        '--rich', 
        action='store_true', 
        help='Muestra el AST en consola usando Rich (Solo aplica para la fase parser)'
    )
    
    terminal.add_argument(
        '--graphviz', 
        action='store_true', 
        help='Exporta el AST a un diagrama de Graphviz (Solo aplica para la fase parser)'
    )
    
    args = terminal.parse_args()

    # ejecutamos la función principal del compilador con los argumentos proporcionados
    compilar(args.fase, args.filename, use_rich=args.rich, use_graphviz=args.graphviz)