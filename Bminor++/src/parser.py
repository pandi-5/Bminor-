# grammar.py (versión actualizada para nuevo AST)
# Librerias
import logging
import sly
from rich import print as rprint
from graphviz import Digraph

# Archivos propios
from model import *
from lexer_mio  import Lexer
from errors import error, errors_detected
from visualizer import build_rich_tree, build_graphviz

def _L(node, lineno):
	node.lineno = lineno
	return node
	
class Parser(sly.Parser):
	log = logging.getLogger()
	log.setLevel(logging.ERROR)
	expected_shift_reduce = 1
	debugfile='grammar.txt'
	
	tokens = Lexer.tokens
	
	# =================================================
	# PROGRAMA
	# =================================================
	
	@_("decl_list")
	def prog(self, p):
		nodo = Program(p.decl_list)
		return _L(nodo, 1)

	# =================================================
	# LISTAS DE DECLARACIONES
	# =================================================
	
	@_("decl decl_list")
	def decl_list(self, p):
		return [p.decl] + p.decl_list
		
	@_("empty")
	def decl_list(self, p):
		return []
		
	# =================================================
	# DECLARACIONES
	# =================================================

	@_("ID ':' type_func ';'")
	@_("ID ':' type_array_sized ';'")
	@_("ID ':' type_simple ';'")
	def decl(self, p):
		nodo = SimpleDecl(p.ID, p[2])
		return _L(nodo, p.lineno)

	@_("decl_init")
	@_("class_decl")	
	def decl(self, p):
		return p[0]
		
	# === DECLARACIONES con inicialización
	
	@_("ID ':' CONSTANT '=' expr ';'")
	@_("ID ':' type_simple '=' expr ';'")
	def decl_init(self, p):
		nodo = InitDecl(p.ID, p[2], p[4])
		return _L(nodo, p.lineno)

	@_("ID ':' type_func '=' '{' opt_stmt_list '}'")	
	@_("ID ':' type_array_sized '=' '{' opt_expr_list '}' ';'")
	def decl_init(self, p):
		nodo = InitDecl(p.ID, p[2], p[5])
		return _L(nodo, p.lineno)

	# =================================================
	# CLASES
	# =================================================

	@_("CLASS ':' ID class_body")	
	def class_decl(self, p):
		nodo = ClassDecl(p.ID, p[3])
		return _L(nodo, p.lineno)

	@_("'{' class_member_list '}'")	
	def class_body(self, p):
		return p.class_member_list
	
	@_("empty")	
	def class_member_list(self, p):
		return []

	@_("class_member class_member_list")	
	def class_member_list(self, p):
		return [p.class_member] + p.class_member_list
	
	@_("decl")	
	@_("decl_init")
	def class_member(self, p):
		return p[0]

	# =================================================
	# STATEMENTS
	# =================================================
	
	@_("stmt_list")
	def opt_stmt_list(self, p):
		return p.stmt_list
		
	@_("empty")
	def opt_stmt_list(self, p):
		return []
		
	@_("stmt stmt_list")
	def stmt_list(self, p):
		return [p.stmt] + p.stmt_list
		
	@_("stmt")
	def stmt_list(self, p):
		return [p.stmt]
		
	@_("open_stmt")
	@_("closed_stmt")
	def stmt(self, p):
		return p[0]

	@_("if_stmt_closed")
	@_("for_stmt_closed")
	@_("while_stmt_closed")
	@_("simple_stmt")
	def closed_stmt(self, p):
		return p[0]

	@_("if_stmt_open")
	@_("for_stmt_open")
	@_("while_stmt_open")
	def open_stmt(self, p):
		return p[0]

	# -------------------------------------------------
	# IF
	# -------------------------------------------------
	
	@_("if_cond closed_stmt ELSE closed_stmt")
	def if_stmt_closed(self, p):
		nodo = If(p.if_cond, p[1], p[3])
		return _L(nodo, p.lineno)
	
	@_("if_cond closed_stmt ELSE if_stmt_open")
	def if_stmt_open(self, p):
		nodo = If(p.if_cond, p[1], p[3])
		return _L(nodo, p.lineno)

	@_("if_cond stmt")
	def if_stmt_open(self, p):
		nodo = If(p.if_cond, p[1], None)
		return _L(nodo, p.lineno)

	@_("IF '(' opt_expr ')'")
	def if_cond(self, p):
		return p.opt_expr
		
	# -------------------------------------------------
	# FOR
	# -------------------------------------------------
	
	@_("for_header closed_stmt")
	def for_stmt_closed(self, p):
		nodo = For(p.for_header, p[1])
		return _L(nodo, p.lineno)

	@_("for_header open_stmt")
	def for_stmt_open(self, p):
		nodo = For(p.for_header, p[1])
		return _L(nodo, p.lineno)

	@_("FOR '(' opt_expr ';' opt_expr ';' opt_expr ')'")
	def for_header(self, p):
		return [p[2], p[4], p[6]]
		
	# -------------------------------------------------
	# WHILE
	# -------------------------------------------------
		
	@_("while_header open_stmt")
	def while_stmt_open(self, p):
		nodo = While(p.while_header, p[1])
		return _L(nodo, p.lineno)
		
	@_("while_header closed_stmt")
	def while_stmt_closed(self, p):
		nodo = While(p.while_header, p[1])
		return _L(nodo, p.lineno)

	@_("WHILE '(' opt_expr ')'")
	def while_header(self, p):
		return p.opt_expr
		
	# -------------------------------------------------
	# SIMPLE STATEMENTS
	# -------------------------------------------------
	
	@_("print_stmt")
	@_("return_stmt")
	@_("break_stmt")
	@_("continue_stmt")
	@_("block_stmt")
	@_("decl")
	@_("expr ';'")
	def simple_stmt(self, p):
		return p[0]

	# PRINT
	@_("PRINT opt_expr_list ';'")
	def print_stmt(self, p):
		nodo = Print(p[1])
		return _L(nodo, p.lineno)
	
	# RETURN
	@_("RETURN opt_expr ';'")
	def return_stmt(self, p):
		nodo = Return(p[1])
		return _L(nodo, p.lineno)

	@_("BREAK ';'")
	def break_stmt(self, p):
		nodo = Break()
		return _L(nodo, p.lineno)

	@_("CONTINUE ';'")
	def continue_stmt(self, p):
		nodo = Continue()
		return _L(nodo, p.lineno)

	# BLOCK
	@_("'{' stmt_list '}'")
	def block_stmt(self, p):
		nodo = Block(p[1])
		return _L(nodo, p.lineno)
		
	# =================================================
	# EXPRESIONES
	# =================================================
	
	@_("empty")
	def opt_expr_list(self, p):
		return []
		
	@_("expr_list")
	def opt_expr_list(self, p):
		return p.expr_list
		
	@_("expr ',' expr_list")
	def expr_list(self, p):
		return [p.expr] + p.expr_list
		
	@_("expr")
	def expr_list(self, p):
		return [p.expr]
		
	@_("empty")
	def opt_expr(self, p):
		return None
		
	@_("expr")
	def opt_expr(self, p):
		return p.expr
		
	# -------------------------------------------------
	# PRIMARY
	# -------------------------------------------------
	
	@_("expr1")
	def expr(self, p):
		return p.expr1
		
	@_("lval  '='  expr1")
	@_("lval ADDEQ expr1")
	@_("lval SUBEQ expr1")
	@_("lval MULEQ expr1")
	@_("lval DIVEQ expr1")
	@_("lval MODEQ expr1")
	def expr1(self, p):
		nodo = Assignment(p.lval, p[1], p.expr1)
		return _L(nodo, p.lineno)
		
	@_("expr2")
	@_("tern_op")
	def expr1(self, p):
		return p[0]
	
	# ----------- TERNARY OPERATOR -------------------

	@_("expr2 '?' tern_op ':' tern_op")
	def tern_op(self, p):
		nodo = TernaryOp(p.expr2, p[2], p[4])
		return _L(nodo, p.lineno)
	
	@_("expr2")
	def tern_op(self, p):
		return p.expr2
		
	# ----------- LVALUES -------------------
	
	@_("ID")
	def lval(self, p):
		node = Id(p.ID)
		return _L(node, p.lineno)
		
	@_("lval index")
	def lval(self, p):
		node = IdIndex(p[0], p[1])
		return _L(node, p.lineno)
	
	@_("THIS '.' ID")
	def lval(self, p):
		node = GetAttr('this', p.ID)
		return _L(node, p.lineno)

	@_("lval '.' ID")
	def lval(self, p):
		node = GetAttr(p[0], p[2])
		return _L(node, p.lineno)
		
	# -------------------------------------------------
	# OPERADORES
	# -------------------------------------------------
	
	@_("expr2 LOR expr3")
	def expr2(self, p):
		node = BinaryOp(p.expr2, p.LOR, p.expr3)
		return _L(node, p.lineno)

	@_("expr3")
	def expr2(self, p):
		return p.expr3
		
	@_("expr3 LAND expr4")
	def expr3(self, p):
		node = BinaryOp(p.expr3, p.LAND, p.expr4)
		return _L(node, p.lineno)
		
	@_("expr4")
	def expr3(self, p):
		return p.expr4
		
	@_("expr4 EQ expr5")
	@_("expr4 NE expr5")
	@_("expr4 LT expr5")
	@_("expr4 LE expr5")
	@_("expr4 GT expr5")
	@_("expr4 GE expr5")
	def expr4(self, p):
		node = BinaryOp(p.expr4, p[1], p.expr5)
		return _L(node, p.lineno)

	@_("expr5")
	def expr4(self, p):
		return p.expr5
		
	@_("expr5 '+' expr6")
	@_("expr5 '-' expr6")
	def expr5(self, p):
		node = BinaryOp(p.expr5, p[1], p.expr6)
		return _L(node, p.lineno)

	@_("expr6")
	def expr5(self, p):
		return p.expr6
		
	@_("expr6 '*' expr7")
	@_("expr6 '/' expr7")
	@_("expr6 '%' expr7")
	def expr6(self, p):
		node = BinaryOp(p.expr6, p[1], p.expr7)
		return _L(node, p.lineno)

	@_("expr7")
	def expr6(self, p):
		return p.expr7
		
	@_("expr7 '^' expr8")
	def expr7(self, p):
		node = BinaryOp(p.expr7, p[1], p.expr8)
		return _L(node, p.lineno)

	@_("expr8")
	def expr7(self, p):
		return p.expr8
		
	@_("'-' expr8")
	@_("LNOT expr8")
	@_("INC expr8")
	@_("DEC expr8")
	def expr8(self, p):
		operador = p[0]
		if operador == '++':
			nodo = UnaryOp('PRE_INC', p.expr8)
		elif operador == '--':
			nodo = UnaryOp('PRE_DEC', p.expr8)
		else:
			nodo = UnaryOp(operador, p.expr8)
		return _L(nodo, p.lineno)

	@_("expr9")
	def expr8(self, p):
		return p.expr9

	@_("expr9 INC")
	@_("expr9 DEC")
	def expr9(self, p):
		operador = p[1]
		if operador == '++':
			nodo = UnaryOp('POST_INC', p.expr9)
		else:
			nodo = UnaryOp('POST_DEC', p.expr9)
		return _L(nodo, p.lineno)

	@_("group")
	def expr9(self, p):
		return p.group
		
	@_("'(' expr ')'")
	def group(self, p):
		return p.expr
		
	@_("ID '(' opt_expr_list ')'")
	def group(self, p):
		nodo = Call(p.ID, p.opt_expr_list)
		return _L(nodo, p.lineno)

	@_("lval '.' ID '(' opt_expr_list ')'")
	def group(self, p):
		nodo = MethodCall(p[0], p[2], p.opt_expr_list) 
		return _L(nodo, p.lineno)

	@_("factor")
	@_("lval")
	@_("object_instantiation")
	def group(self, p):
		return p[0]

	# INSTANCIA DE UN OBJETO
	@_("NEW ID '(' opt_expr_list ')'")
	def object_instantiation(self, p):
		nodo = NewInstance(p.ID, p.opt_expr_list)
		return _L(nodo, p.lineno)

	# LISTA DE INDICES
	@_("index_list index")
	def index_list(self, p):
		return p.index_list + [p.index]

	@_("index")
	def index_list(self, p):
		return [p.index]

	# INDICE DE ARREGLO
	@_("'[' expr ']'")
	def index(self, p):
		return p.expr

	# -------------------------------------------------
	# FACTORES
	# -------------------------------------------------
	
	@_("ID")
	def factor(self, p):
		node = Id(p.ID)
		return _L(node, p.lineno)
		
	@_("INTEGER_LITERAL")
	def factor(self, p):
		nodo = Literal('INTEGER_LITERAL', int(p[0]))
		return _L(nodo, p.lineno)

	@_("FLOAT_LITERAL")
	def factor(self, p):
		nodo = Literal('FLOAT_LITERAL', float(p[0]))
		return _L(nodo, p.lineno)
		
	@_("CHAR_LITERAL")
	def factor(self, p):
		texto_limpio = p.CHAR_LITERAL[1:-1]
		nodo = Literal('CHAR_LITERAL', texto_limpio)
		return _L(nodo, p.lineno)
		
	@_("STRING_LITERAL")
	def factor(self, p):
		texto_limpio = p.STRING_LITERAL[1:-1]
		nodo = Literal('STRING_LITERAL', texto_limpio)
		return _L(nodo, p.lineno)
		
	@_("TRUE")
	def factor(self, p):
		nodo = Literal('BOOLEAN', True)
		return _L(nodo, p.lineno)

	@_("FALSE")
	def factor(self, p):
		nodo = Literal('BOOLEAN', False)
		return _L(nodo, p.lineno)

	@_("THIS")
	def factor(self, p):
		nodo = Id('this')
		return _L(nodo, p.lineno)
		
	# =================================================
	# TIPOS
	# =================================================
	
	@_("INTEGER")
	@_("FLOAT")
	@_("BOOLEAN")
	@_("CHAR")
	@_("STRING")
	@_("VOID")
	@_("ID")
	def type_simple(self, p):
		return p[0]
		
	@_("ARRAY '[' ']' type_simple")
	@_("ARRAY '[' ']' type_array")
	def type_array(self, p):
		nodo = Array(p[3], None)
		return _L(nodo, p.lineno)
		
	@_("ARRAY index type_simple")
	@_("ARRAY index type_array_sized")
	def type_array_sized(self, p):
		nodo = Array(p[2], p[1])
		return _L(nodo, p.lineno)
		
	@_("FUNCTION type_simple '(' opt_param_list ')'")
	@_("FUNCTION type_array_sized '(' opt_param_list ')'")
	def type_func(self, p):
		nodo = Function(p[1], p.opt_param_list)
		return _L(nodo, p.lineno)
		
	@_("empty")
	def opt_param_list(self, p):
		return []
		
	@_("param_list")
	def opt_param_list(self, p):
		return p.param_list
		
	@_("param_list ',' param")
	def param_list(self, p):
		return p.param_list + [p.param]
		
	@_("param")
	def param_list(self, p):
		return [p.param]

	@_("ID ':' type_array_sized")	
	@_("ID ':' type_array")
	@_("ID ':' type_simple")
	def param(self, p):
		nodo = ParamDecl(p.ID, p[2])
		return _L(nodo, p.lineno)
		
	# =================================================
	# UTILIDAD: EMPTY
	# =================================================
	
	@_("")
	def empty(self, p):
		pass
		
	def error(self, p):
		code_lines = self.code.splitlines()
		linetxt = code_lines[p.lineno - 1] if p and p.lineno <= len(code_lines) else ''
		
		inicio_linea = self.code.rfind('\n', 0, p.index) + 1
		columna = p.index - inicio_linea

		if linetxt:
			linea_error = linetxt[:columna] + f"[bold white on red]{str(p.value)}[/bold white on red]" + linetxt[columna + len(str(p.value)):]
		else:
			linea_error = ""

		lineno = p.lineno if p else 'EOF'
		value = repr(p.value) if p else 'EOF'
		error(f'Syntax error at {value}', lineno, content_line=linea_error)
		
# ===================================================
# Utilidad: convertir algo en bloque si no lo es
# ===================================================
def as_block(x):
	if isinstance(x, Block):
		return x
	if isinstance(x, list):
		return Block(x)
	return Block([x])
	
	
# Convertir AST a diccionario
def ast_to_dict(node):
	if isinstance(node, list):
		return [ast_to_dict(item) for item in node]
	elif hasattr(node, "__dict__"):
		return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
	else:
		return node

# ===================================================
# test
# ===================================================
def parse(txt):
	l = Lexer()
	p = Parser()
	p.code = txt
	return p.parse(l.tokenize(txt))
	
	
if __name__ == '__main__':
    import sys, json, os
    import argparse  # Importamos el gestor de argumentos de Python
    
    # CONFIGURACIÓN DE LOS ARGUMENTOS DE TERMINAL
    parser = argparse.ArgumentParser(description="Compilador B-Minor AST Builder")
    parser.add_argument("filename", nargs="?", help="Ruta al archivo .bpp a compilar")

    # Banderas opcionales (action="store_true" significa que si las pones, valen True)
    parser.add_argument("--rich", action="store_true", help="Muestra el AST en la consola usando Rich")
    parser.add_argument("--graphviz", action="store_true", help="Genera una imagen PNG del AST con Graphviz")
    args = parser.parse_args()
    
    filename = args.filename
    
    if sys.platform == 'ios' and not filename:
        from file_picker import file_picker_dialog
        filename = file_picker_dialog(
            title='Seleccionar un archivo',
            root_dir='./test/',
            file_pattern='^.*[.]bpp'
        )
        
    if not filename:
        parser.print_help()
        sys.exit("\nError: Debes proporcionar un archivo.")

    # --- 3. COMPILACIÓN ---
    if filename:
        txt = open(filename, encoding='utf-8').read()
        ast = parse(txt)

        if not errors_detected() and ast is not None:
            print("\nAST generado correctamente.")
            
            # Si el usuario no puso ni --rich ni --graphviz
            if not args.rich and not args.graphviz:
                print("Usa las banderas --rich o --graphviz para visualizar el árbol.")
                
            if args.rich:
                print("ÁRBOL EN CONSOLA\n")
                arbol_rich = build_rich_tree(ast)
                rprint(arbol_rich)
                
            if args.graphviz:
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
                
        else:
            print("Errores sintácticos. No se pudo generar el AST.")