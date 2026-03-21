# grammar.py (versión actualizada para nuevo AST)
import logging
import sly
from rich import print

from model import *
from lexer_mio  import Lexer
from errors import error, errors_detected

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
		return p.decl_list
	
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
		return ('SIMPLE_DECL', p.ID, p[2])

	@_("decl_init")
	@_("class_decl")	
	def decl(self, p):
		return p[0]
		
	# === DECLARACIONES con inicialización
	
	@_("ID ':' CONSTANT '=' expr ';'")
	@_("ID ':' type_simple '=' expr ';'")
	def decl_init(self, p):
		return ('INIT_DECL', p.ID, p[2], p.expr)

	@_("ID ':' type_func '=' '{' opt_stmt_list '}'")	
	@_("ID ':' type_array_sized '=' '{' opt_expr_list '}' ';'")
	def decl_init(self, p):
		return ('INIT_DECL', p.ID, p[2], p[5])

	# =================================================
	# CLASES
	# =================================================

	@_("CLASS ':' ID class_body")	
	def class_decl(self, p):
		return ('CLASS_DECL', p.ID, p.class_body)

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
		return ('IF', p.if_cond, p[1], p[3])
	
	@_("if_cond closed_stmt ELSE if_stmt_open")
	def if_stmt_open(self, p):
		return ('IF', p.if_cond, p[1], p[3])

	@_("if_cond stmt")
	def if_stmt_open(self, p):
		return ('IF', p.if_cond, p.stmt, None)

	@_("IF '(' opt_expr ')'")
	def if_cond(self, p):
		return p.opt_expr
		
	# -------------------------------------------------
	# FOR
	# -------------------------------------------------
	
	@_("for_header closed_stmt")
	def for_stmt_closed(self, p):
		return ('FOR', p.for_header, p.closed_stmt)

	@_("for_header open_stmt")
	def for_stmt_open(self, p):
		return ('FOR', p.for_header, p.open_stmt)

	@_("FOR '(' opt_expr ';' opt_expr ';' opt_expr ')'")
	def for_header(self, p):
		return (p[2], p[4], p[6])
		
	# -------------------------------------------------
	# WHILE
	# -------------------------------------------------
		
	@_("while_cond open_stmt")
	def while_stmt_open(self, p):
		return ('WHILE', p.while_cond, p.open_stmt)
		
	@_("while_cond closed_stmt")
	def while_stmt_closed(self, p):
		return ('WHILE', p.while_cond, p.closed_stmt)
	
	@_("WHILE '(' opt_expr ')'")
	def while_cond(self, p):
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
		return ('PRINT', p.opt_expr_list)
		
	# RETURN
	@_("RETURN opt_expr ';'")
	def return_stmt(self, p):
		return ('RETURN', p.opt_expr)

	@_("BREAK ';'")
	def break_stmt(self, p):
		return ('BREAK',)		# Se deja como tupla para facilitar acceso

	@_("CONTINUE ';'")
	def continue_stmt(self, p):
		return ('CONTINUE',)	# Se deja como tupla para facilitar acceso

	# BLOCK
	@_("'{' stmt_list '}'")
	def block_stmt(self, p):
		return p.stmt_list
		
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
		return [p.expr]
		
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
		return (p[1], p[0], p[2])
		
	@_("expr2")
	@_("tern_op")
	def expr1(self, p):
		return p[0]
	
	# ----------- TERNARY OPERATOR -------------------

	@_("expr2 '?' tern_op ':' tern_op")
	def tern_op(self, p):
		return ('TERNARY', p.expr2, p[2], p[4])
	
	@_("expr2")
	def tern_op(self, p):
		return p.expr2
		
	# ----------- LVALUES -------------------
	
	@_("ID")
	def lval(self, p):
		return ('ID', p.ID)
		
	@_("ID index")
	def lval(self, p):
		return ('INDEX_ID', p.ID, p[1])
	
	@_("THIS '.' ID")
	def lval(self, p):
		return ('GET_ATTR', 'this', p.ID)
		
	# -------------------------------------------------
	# OPERADORES
	# -------------------------------------------------
	
	@_("expr2 LOR expr3")
	def expr2(self, p):
		return (p.LOR, p.expr2, p.expr3)
		
	@_("expr3")
	def expr2(self, p):
		return p.expr3
		
	@_("expr3 LAND expr4")
	def expr3(self, p):
		return (p.LAND, p.expr3, p.expr4)
		
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
		return (p[1], p[0], p[2])

	@_("expr5")
	def expr4(self, p):
		return p.expr5 
		
	@_("expr5 '+' expr6")
	@_("expr5 '-' expr6")
	def expr5(self, p):
		return (p[1], p.expr5, p.expr6)
		
	@_("expr6")
	def expr5(self, p):
		return p.expr6
		
	@_("expr6 '*' expr7")
	@_("expr6 '/' expr7")
	@_("expr6 '%' expr7")
	def expr6(self, p):
		return (p[1], p.expr6, p.expr7)
		
	@_("expr7")
	def expr6(self, p):
		return p.expr7
		
	@_("expr7 '^' expr8")
	def expr7(self, p):
		return (p[1], p.expr7, p.expr8)
		
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
			return ('PRE_INC', p.expr8)
		elif operador == '--':
			return ('PRE_DEC', p.expr8)
		else:
			return (operador, p.expr8)
		
	@_("expr9")
	def expr8(self, p):
		return p.expr9

	@_("expr9 INC")
	@_("expr9 DEC")
	def expr9(self, p):
		operador = p[1]
		if operador == '++':
			return ('POST_INC', p.expr9)
		else:
			return ('POST_DEC', p.expr9)

	@_("group")
	def expr9(self, p):
		return p.group
		
	@_("'(' expr ')'")
	def group(self, p):
		return p.expr
		
	@_("ID '(' opt_expr_list ')'")
	def group(self, p):
		return ('CALL', p.ID, p.opt_expr_list)
		
	@_("ID index")
	def group(self, p):
		return ('INDEX_ID', p.ID, p[1])

	@_("factor")
	@_("member_access")
	@_("object_instantiation")
	def group(self, p):
		return p[0]

	# INSTANCIA DE UN OBJETO
	@_("NEW ID '(' opt_expr_list ')'")
	def object_instantiation(self, p):
		return('NEW_INSTANCE', p.ID, p.opt_expr_list)
	
	# ACCESO A MIEMBRO DE CLASE
	@_("ID '.' ID")
	@_("member_access '.' ID")
	def member_access(self, p):
		return('GET_ATTR', p[0], p[2])
	
	@_("THIS '.' ID")
	def member_access(self, p):
		return('GET_ATTR', 'this', p[2])
	
	@_("member_access '(' opt_expr_list ')'")
	def member_access(self, p):
		return('METHOD_CALL', p[0], p[2])
	
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
		return ('ID', p.ID)
		
	@_("INTEGER_LITERAL")
	def factor(self, p):
		return ('INTEGER_LITERAL', int(p[0]))
		
	@_("FLOAT_LITERAL")
	def factor(self, p):
		return ('FLOAT_LITERAL', float(p[0]))
		
	@_("CHAR_LITERAL")
	def factor(self, p):
		texto_limpio = p.CHAR_LITERAL[1:-1]
		return ('CHAR_LITERAL', texto_limpio)
		
	@_("STRING_LITERAL")
	def factor(self, p):
		texto_limpio = p.STRING_LITERAL[1:-1]
		return ('STRING_LITERAL', texto_limpio)
		
	@_("TRUE")
	def factor(self, p):
		return ('BOOLEAN', True)
	
	@_("FALSE")
	def factor(self, p):
		return ('BOOLEAN', False)

	@_("THIS")
	def factor(self, p):
		return ('THIS',)
		
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
		return('ARRAY', p[3])
		
	@_("ARRAY index type_simple")
	@_("ARRAY index type_array_sized")
	def type_array_sized(self, p):
		return('ARRAY', p[1], p[2])
		
	@_("FUNCTION type_simple '(' opt_param_list ')'")
	@_("FUNCTION type_array_sized '(' opt_param_list ')'")
	def type_func(self, p):
		return('FUNCTION', p[1], p[3])
		
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
		
	@_("ID ':' type_simple")
	def param(self, p):
		return ('PARAM_DECL', p.ID, p.type_simple)
		
	@_("ID ':' type_array")
	def param(self, p):
		return ('PARAM_DECL', p.ID, p.type_array)
		
	@_("ID ':' type_array_sized")
	def param(self, p):
		return ('PARAM_DECL', p.ID, p.type_array_sized)
		
	# =================================================
	# UTILIDAD: EMPTY
	# =================================================
	
	@_("")
	def empty(self, p):
		pass
		
	def error(self, p):
		lineno = p.lineno if p else 'EOF'
		value = repr(p.value) if p else 'EOF'
		error(f'Syntax error at {value}', lineno)
		
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
	return p.parse(l.tokenize(txt))
	
	
if __name__ == '__main__':
	import sys, json
	
	if sys.platform != 'ios':
	
		if len(sys.argv) != 2:
			raise SystemExit("Usage: python gparse.py <filename>")
			
		filename = sys.argv[1]
		
	else:
		from file_picker import file_picker_dialog
		
		filename = file_picker_dialog(
			title='Seleccionar una archivo',
			root_dir='./test/',
			file_pattern='^.*[.]bpp'
		)
		
	if filename:
		txt = open(filename, encoding='utf-8').read()
		ast = parse(txt)
		
		if not errors_detected():
			print(ast)