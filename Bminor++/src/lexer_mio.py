# lexer.py
from rich import print
import sly

#------------------------------ CLASE LEXER -------------------------------------------------------

class Lexer(sly.Lexer):
    tokens = {
        # Palabras Reservadas
        ARRAY, BOOLEAN, CHAR, ELSE, TRUE, FALSE, FLOAT, FOR,
        FUNCTION, IF, INTEGER, PRINT, RETURN, STRING, AUTO,
        VOID, WHILE, CLASS, NEW, THIS, CONSTANT, BREAK, CONTINUE,

        # Operadores de Relacion
        LT, LE, GT, GE, EQ, NE, LAND, LOR, LNOT, INC, DEC,

        # Operadores de Asignacion
        ADDEQ, SUBEQ, MULEQ, DIVEQ, MODEQ,

        # Identidicador
        ID,

        # Literales
        INTEGER_LITERAL, FLOAT_LITERAL, CHAR_LITERAL,
        STRING_LITERAL, BOOLEAN_LITERAL
    }


    # LITERALES
    FLOAT_LITERAL   = r'(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE][+-]?[0-9]+)?)|([0-9]+[eE][+-]?[0-9]+)'
    INTEGER_LITERAL = r'[1-9][0-9]*|0'
    STRING_LITERAL  = r'"(\\[abefnrtv\'"\\]|[\x20-\x21\x23-\x5B\x5D-\x7E])*"'
    CHAR_LITERAL    = r"'(\\([abefnrtv'\"\\]|0x[0-9A-F]{2})|[\x20-\x26\x28-\x5B\x5D-\x7E])'"

    # Definición de Tokens (Identificador)
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # PALABRAS RESERVADAS
    ID['array']     = ARRAY
    ID['auto']      = AUTO
    ID['boolean']   = BOOLEAN
    ID['char']      = CHAR
    ID['else']      = ELSE
    ID['true']      = TRUE
    ID['false']     = FALSE
    ID['float']     = FLOAT
    ID['for']       = FOR
    ID['function']  = FUNCTION
    ID['func']      = FUNCTION
    ID['if']        = IF
    ID['integer']   = INTEGER
    ID['print']     = PRINT
    ID['return']    = RETURN
    ID['string']    = STRING
    ID['void']      = VOID
    ID['while']     = WHILE
    ID['class']     = CLASS
    ID['new']       = NEW
    ID['this']      = THIS
    ID['constant']  = CONSTANT
    ID['break']     = BREAK
    ID['continue']  = CONTINUE

    # OPERADORES DE RELACION
    LE   = r'<='
    GE   = r'>='
    EQ   = r'=='
    NE   = r'\!='
    LT   = r'<'
    GT   = r'>'
    LAND = r'\&\&'
    LOR  = r'\|\|'
    LNOT = r'\!'
    INC  = r'\+\+'
    DEC  = r'\-\-'

    # OPERADORES DE ASIGNACION
    ADDEQ = r'\+='
    SUBEQ = r'\-='
    MULEQ = r'\*='
    DIVEQ = r'\/='
    MODEQ = r'\%='

    @_(r'//.*\n')
    def ignore_cppcomment(self, t):
        self.lineno += 1
    
    @_(r'/\*(.|\n)*?\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'/\*(.|\n)*')
    def ignore_comment_error(self, t):
        print(f"Línea {self.lineno}: ERROR - Comentario de bloque sin cerrar (/*)")
        self.lineno += t.value.count('\n')

    @_(r"'([^'\n]|\\.)*?'")
    def len_char_error(self, t):
        print(f"Línea {self.lineno}: ERROR - Caracter demasiado largo o inválido {t.value}")

    @_(r"'([^'\n]|\\.)*")
    def ignore_char_error(self, t):
        print(f"Línea {self.lineno}: ERROR - Caracter sin cerrar (')")

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        # Manejo de errores
        print(f"{self.lineno}: Carácter '{t.value[0]}' ilegal")
        self.index += 1

    literals = '+-*/%^=,.:;()[]{}`'

    # Patrones a Ignorar
    ignore = ' \t\r'        # Whitespace

#------------------------------ FUNCION GENERAR TOKENS --------------------------------------------

def tokenize(source):
    lex = Lexer()

    for tok in lex.tokenize(source):
        print(tok)

#------------------------------ FUNCION MAIN ------------------------------------------------------

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: python lexer.py filename')
        raise SystemExit
    
    txt = open(sys.argv[1], encoding='utf-8').read()
    tokenize(txt)