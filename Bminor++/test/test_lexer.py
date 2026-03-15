from lexer import Lexer

def test_keywords ():
    lex = Lexer()
    tokens = list(lex.tokenize("if while for array boolean char else true false function integer print return string void float"))

    assert len(tokens) == 16

    assert tokens[0].type == "IF"
    assert tokens[0].value == "if"

    assert tokens[1].type == "WHILE"
    assert tokens[1].value == "while"

    assert tokens[2].type == "FOR"
    assert tokens[2].value == "for"

    assert tokens[3].type == "ARRAY"
    assert tokens[3].value == "array"

    assert tokens[4].type == "BOOLEAN"
    assert tokens[4].value == "boolean"

    assert tokens[5].type == "CHAR"
    assert tokens[5].value == "char"

    assert tokens[6].type == "ELSE"
    assert tokens[6].value == "else"

    assert tokens[7].type == "TRUE"
    assert tokens[7].value == "true"

    assert tokens[8].type == "FALSE"
    assert tokens[8].value == "false"

    assert tokens[9].type == "FUNCTION"
    assert tokens[9].value == "function"

    assert tokens[10].type == "INTEGER"
    assert tokens[10].value == "integer"

    assert tokens[11].type == "PRINT"
    assert tokens[11].value == "print"

    assert tokens[12].type == "RETURN"
    assert tokens[12].value == "return"

    assert tokens[13].type == "STRING"
    assert tokens[13].value == "string"

    assert tokens[14].type == "VOID"
    assert tokens[14].value == "void"

    assert tokens[15].type == "FLOAT"
    assert tokens[15].value == "float"


def test_relation_op ():
    lex = Lexer()
    tokens = list(lex.tokenize(">= <= > < == || && ! != ++ --"))

    assert len(tokens) == 11

    assert tokens[0].type == "GE"
    assert tokens[0].value == ">="

    assert tokens[1].type == "LE"
    assert tokens[1].value == "<="

    assert tokens[2].type == "GT"
    assert tokens[2].value == ">"

    assert tokens[3].type == "LT"
    assert tokens[3].value == "<"

    assert tokens[4].type == "EQ"
    assert tokens[4].value == "=="

    assert tokens[5].type == "LOR"
    assert tokens[5].value == "||"

    assert tokens[6].type == "LAND"
    assert tokens[6].value == "&&"

    assert tokens[7].type == "LNOT"
    assert tokens[7].value == "!"

    assert tokens[8].type == "NE"
    assert tokens[8].value == "!="

    assert tokens[9].type == "INC"
    assert tokens[9].value == "++"

    assert tokens[10].type == "DEC"
    assert tokens[10].value == "--"


def test_asign_op ():
    lex = Lexer()
    tokens = list(lex.tokenize("+= -= *= /= %="))

    assert len(tokens) == 5

    assert tokens[0].type == "ADDEQ"
    assert tokens[0].value == "+="

    assert tokens[1].type == "SUBEQ"
    assert tokens[1].value == "-="

    assert tokens[2].type == "MULEQ"
    assert tokens[2].value == "*="

    assert tokens[3].type == "DIVEQ"
    assert tokens[3].value == "/="

    assert tokens[4].type == "MODEQ"
    assert tokens[4].value == "%="


def test_id ():
    lex = Lexer()
    tokens = list(lex.tokenize("abc ABC abc123 _abc a_b_c A_bc_123"))

    assert len(tokens) == 6

    assert tokens[0].type == "ID"
    assert tokens[0].value == "abc"

    assert tokens[1].type == "ID"
    assert tokens[1].value == "ABC"

    assert tokens[2].type == "ID"
    assert tokens[2].value == "abc123"

    assert tokens[3].type == "ID"
    assert tokens[3].value == "_abc"

    assert tokens[4].type == "ID"
    assert tokens[4].value == "a_b_c"

    assert tokens[5].type == "ID"
    assert tokens[5].value == "A_bc_123"


def test_integer_literal ():
    lex = Lexer()
    tokens = list(lex.tokenize("0 1299 234"))

    assert len(tokens) == 3

    assert tokens[0].type == "INTEGER_LITERAL"
    assert tokens[0].value == "0"

    assert tokens[1].type == "INTEGER_LITERAL"
    assert tokens[1].value == "1299"

    assert tokens[2].type == "INTEGER_LITERAL"
    assert tokens[2].value == "234"


def test_float_literal ():
    lex = Lexer()
    tokens = list(lex.tokenize("0.123 .123 12.3 0.2e+123 123.E-12 1.e3 10e-2"))

    assert len(tokens) == 7

    assert tokens[0].type == "FLOAT_LITERAL"
    assert tokens[0].value == "0.123"

    assert tokens[1].type == "FLOAT_LITERAL"
    assert tokens[1].value == ".123"

    assert tokens[2].type == "FLOAT_LITERAL"
    assert tokens[2].value == "12.3"

    assert tokens[3].type == "FLOAT_LITERAL"
    assert tokens[3].value == "0.2e+123"

    assert tokens[4].type == "FLOAT_LITERAL"
    assert tokens[4].value == "123.E-12"

    assert tokens[5].type == "FLOAT_LITERAL"
    assert tokens[5].value == "1.e3"

    assert tokens[6].type == "FLOAT_LITERAL"
    assert tokens[6].value == "10e-2"


def test_char_literal ():
    lex = Lexer()
    entrada = r"'h' '\n' '\"' ' ' '\a'"
    tokens = list(lex.tokenize(entrada))

    assert len(tokens) == 5

    assert tokens[0].type == "CHAR_LITERAL"
    assert tokens[0].value == "'h'"

    assert tokens[1].type == "CHAR_LITERAL"
    assert tokens[1].value == r"'\n'"

    assert tokens[2].type == "CHAR_LITERAL"
    assert tokens[2].value == r"'\"'"

    assert tokens[3].type == "CHAR_LITERAL"
    assert tokens[3].value == "' '"

    assert tokens[4].type == "CHAR_LITERAL"
    assert tokens[4].value == r"'\a'"


def test_string_literal ():
    lex = Lexer()
    entrada = r'"\'" "hola mundo" "@?!#$%&/()" "\n\e\f" "\\"'
    tokens = list(lex.tokenize(entrada))

    assert len(tokens) == 5

    assert tokens[0].type == "STRING_LITERAL"
    assert tokens[0].value == r'"\'"'

    assert tokens[1].type == "STRING_LITERAL"
    assert tokens[1].value == '"hola mundo"'

    assert tokens[2].type == "STRING_LITERAL"
    assert tokens[2].value == '"@?!#$%&/()"'

    assert tokens[3].type == "STRING_LITERAL"
    assert tokens[3].value == r'"\n\e\f"'

    assert tokens[4].type == "STRING_LITERAL"
    assert tokens[4].value == r'"\\"'


def test_unterminated_comment():
    lex = Lexer()
    entrada = "if x /* comentario infinito"
    tokens = list(lex.tokenize(entrada))

    assert len(tokens) == 2
    assert tokens[0].type == "IF"
    assert tokens[1].type == "ID"


def test_unterminated_char(capsys):
    lex = Lexer()
    entrada = "integer x = 'a" 
    tokens = list(lex.tokenize(entrada))

    assert len(tokens) == 3 

    assert tokens[0].type == "INTEGER"
    assert tokens[0].value == "integer"

    assert tokens[1].type == "ID"
    assert tokens[1].value == "x"

    assert tokens[2].type == "="
    assert tokens[2].value == "="    