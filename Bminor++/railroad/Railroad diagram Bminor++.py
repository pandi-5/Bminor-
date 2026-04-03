from railroad import Diagram, Choice, Terminal, NonTerminal, Sequence, Skip

# Funciones de utilidad para limpiar el código
def t(x): return Terminal(x)
def n(x): return NonTerminal(x)

prog = Diagram(n("decl_list"), t("EOF"))

class_decl = Diagram(
    t("CLASS"),
    t(":"),
    t("ID"),
    n("class_body")
)

class_body = Diagram(
    t("{"),
    n("class_member_list"),
    t("}")
)

class_member_list = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("class_member"),
            n("class_member_list")
        )
    )
)

class_member = Diagram(
    Choice(0,
        n("decl"),
        n("decl_init")
    )
)

decl_list = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("decl"), 
            n("decl_list"))
    )
)

decl = Diagram(
    Choice(0,
        Sequence(
            t("ID"), 
            t(":"),
            Choice(0, 
                n("type_simple"), 
                n("type_array_sized"), 
                n("type_func")),
                t(";")
        ),
        n("class_decl"),
        n("decl_init")
    )
)

decl_init = Diagram(
    t("ID"), 
    t(":"),
    Choice(0,
        Sequence(
            Choice(0,
                Sequence(
                    n("type_simple"),
                    t("="), 
                    n("expr")
                ),
                Sequence(
                    n("type_array_sized"), 
                    t("="), 
                    t("{"), 
                    n("opt_expr_list"), 
                    t("}")
                )
            ),
            t(";")
        ),
        Sequence(
            n("type_func"), 
            t("="), 
            t("{"), 
            n("opt_stmt_list"), 
            t("}")
        )
    )
)

opt_stmt_list = Diagram(
    Choice(0,
        Skip(),
        n("stmt_list")
    )
)

stmt_list = Diagram(
    n("stmt"),
    Choice(0,
        Skip(),
        n("stmt_list")
    )
)

stmt = Diagram(
    Choice(0,
        n("open_stmt"),
        n("closed_stmt")
    )
)

closed_stmt = Diagram(
    Choice(0,
        n("if_stmt_closed"),
        n("for_stmt_closed"),
        n("while_stmt_closed"),
        n("simple_stmt")
    )
)

open_stmt = Diagram(
    Choice(0,
        n("if_stmt_open"),
        n("for_stmt_open"),
        n("while_stmt_open")
    )
)

if_cond = Diagram(
    t("IF"),
    t("("),
    n("opt_expr"),
    t(")")
)

if_stmt_closed = Diagram(
    n("if_cond"),
    n("closed_stmt"),
    t("ELSE"),
    n("closed_stmt")
)

if_stmt_open = Diagram(
    n("if_cond"),
    Choice(0,
        n("stmt"),
        Sequence(
            n("closde_stmt"),
            t("ELSE"),
            n("if_stmt_open")
        )
    )
)

for_header = Diagram(
    t("FOR"),
    t("("),
    n("opt_expr"),
    t(";"),
    n("opt_expr"),
    t(";"),
    n("opt_expr"),
    t(")")
)

for_stmt_open = Diagram(
    n("for_header"),
    n("open_stmt")
)

for_stmt_closed = Diagram(
    n("for_header"),
    n("closed_stmt")
)

while_header = Diagram(
    t("WHILE"),
    t("("),
    n("opt_expr"),
    t(")")
)

while_stmt_open = Diagram(
    n("while_header"),
    n("open_stmt")
)

while_stmt_closed = Diagram(
    n("while_header"),
    n("closed_stmt")
)

simple_stmt = Diagram(
    Choice(0,
        n("print_stmt"),
        n("return_stmt"),
        n("block_stmt"),
        n("decl"),
        Sequence(
            n("expr"),
            t(";")
        )
    )
) 

print_stmt = Diagram(
    t("PRINT"),
    n("opt_expr_list"),
    t(";")
)

return_stmt = Diagram(
    t("RETURN"),
    n("opt_expr_list"),
    t(";")
)

block_stmt = Diagram(
    t("{"),
    n("stmt_list"),
    t("}")
)

opt_expr_list = Diagram(
    Choice(0,
        Skip(),
        n("expr_list")
    )
)

expr_list = Diagram(
    n("expr"),
    Choice(0,
        Skip(),
        Sequence(
            t(","),
            n("expr_list")
        )
    )
)

opt_expr = Diagram(
    Choice(0,
        Skip(),
        n("expr")
    )
)

expr = Diagram(
    n("expr1")
)

expr1 = Diagram(
    Choice(0,
        Sequence(
            n("lval"),
            Choice(0,
                t("="),
                t("ADDEQ"),
                t("SUBEQ"),
                t("MULEQ"),
                t("DIVEQ"),
                t("MODEQ")
            ),
            n("expr1")
        ),
        n("tern_op"),
        n("expr2")
    )
)

tern_op = Diagram(
    n("expr2"),
    Choice(0,
        Skip(),
        Sequence(
            t("?"),
            n("tern_op"),
            t(":"),
            n("tern_op")
        )
    )
)

lval = Diagram(
    Choice(0,
        Sequence(
            t("ID"),
            Choice(0,
                Skip(),
                n("index")
            )
        ),
        Sequence(
            t("THIS"),
            t("."),
            t("ID")
        )    
    )
)

expr2 = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("expr2"),
            t("LOR")
        )
    ),
    n("expr3")
)

expr3 = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("expr3"),
            t("LAND")
        )
    ),
    n("expr4")
)

expr4 = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("expr4"),
            Choice(0,
                t("EQ"),
                t("NE"),
                t("LT"),
                t("LE"),
                t("GT"),
                t("GE")
            )
        )
    ),
    n("expr5")
)

expr5 = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("expr5"),
            Choice(0,
                t("+"),
                t("-")
            )
        )
    ),
    n("expr6")
)

expr6 = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("expr6"),
            Choice(0,
                t("*"),
                t("/"),
                t("%")
            )
        )
    ),
    n("expr7")
)

expr7 = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("expr7"),
            t("^")
        )
    ),
    n("expr8")
)

expr8 = Diagram(
    Choice(0,
        Sequence(
            Choice(0,
                t("-"),
                t("NOT"),
                t("INC"),
                t("DEC")
            ),
            n("expr8")
        ),
        n("expr9")
    )
)

expr9 = Diagram(
    Choice(0,
        Sequence(
            n("expr9"),
            Choice(0,
                t("INC"),
                t("DEC")
            )
        ),
        n("group")
    )
)

group = Diagram(
    Choice(0,
        Sequence(
            t("("),
            n("expr"),
            t(")",)
        ),
        Sequence(
            t("ID"),
            Choice(0,
                Sequence(
                    t("("),
                    n("opt_expr_list"),
                    t(")")
                ),
                n("index")
            )
        ),
        n("factor"),
        n("object_instantiation"),
        n("member_access")
    )
)

object_instantiation = Diagram(
    t("NEW"),
    t("ID"),
    t("("),
    n("opt_expr_list"),
    t(")"),
)

member_access = Diagram(
    Choice(0,
        Sequence(
            Choice(0,
                t("ID"),
                t("THIS")
            ),
            t("."),
            t("ID")
        ),
        Sequence(
            n("member_access"),
            Choice(0,
                Sequence(
                    t("."),
                    t("ID")
                ),
                Sequence(
                    t("("),
                    n("opt_expr_list"),
                    t(")")
                )
            )
        )
    )
)

index_list = Diagram(
    Choice(0,
        Skip(),
        n("index_list")
    ),
    n("index")
)

index = Diagram(
    t("["),
    n("expr"),
    t("]")
)

factor = Diagram(
    Choice(0,
        t("ID"),
        t("INTEGER_LITERAL"),
        t("FLOAT_LITERAL"),
        t("CHAR_LITERAL"),
        t("STRING_LITERAL"),
        t("TRUE"),
        t("FALSE"),
        t("THIS")
    )
)

type_simple = Diagram(
    Choice(0,
        t("INTEGER"),
        t("FLOAT"),
        t("BOOLEAN"),
        t("CHAR"),
        t("STRING"),
        t("VOID"),
        t("ID")
    )
)

type_array = Diagram(
    t("ARRAY"),
    t("["),
    t("]"),
    Choice(0,
        n("type_simple"),
        n("type_array")
    )
)

type_array_sized = Diagram(
    t("ARRAY"),
    n("index"),
    Choice(0,
        n("type_simple"),
        n("type_array_sized")
    )
)

type_func = Diagram(
    t("FUNCTION"),
    Choice(0,
        n("type_simple"),
        n("type_array_sized")
    ),
    t("("),
    n("opt_param_list"),
    t(")")
)

opt_param_list = Diagram(
    Choice(0,
        Skip(),
        n("param_list")
    )
)

param_list = Diagram(
    Choice(0,
        Skip(),
        Sequence(
            n("param_list"),
            t(",")
        )
    ),
    n("param")
)

param = Diagram(
    t("ID"),
    t(":"),
    Choice(0,
        n("type_simple"),
        n("type_array"),
        n("type_array_sized")
    )
)


Diagramas = [
    ("prog:", prog), ("decl_list:", decl_list), ("decl:", decl), ("decl_init:", decl_init), 
    ("class_decl:", class_decl), ("class_body:", class_body), ("class_member_list:", class_member_list),
    ("class_member:", class_member), ("opt_stmt_list:", opt_stmt_list), ("stmt_list:", stmt_list),
    ("stmt:", stmt), ("closed_stmt:", closed_stmt), ("open_stmt:", open_stmt), ("if_cond:", if_cond),
    ("if_stmt_closed:", if_stmt_closed), ("if_stmt_open:", if_stmt_open), ("for_header:", for_header), 
    ("for_stmt_closed:", for_stmt_closed), ("for_stmt_open:", for_stmt_open),
    ("while_header:", while_header), ("while_stmt_closed:", while_stmt_closed),
    ("while_stmt_open:", while_stmt_open), ("simple_stmt:", simple_stmt),
    ("print_stmt:", print_stmt), ("return_stmt:", return_stmt), ("block_stmt:", block_stmt),
    ("opt_expr_list:", opt_expr_list ), ("expr_list:", expr_list), ("opt_expr:", opt_expr),
    ("expr:", expr), ("expr1:", expr1), ("lval:", lval), ("tern_op:", tern_op), ("expr2:", expr2),
    ("expr3:", expr3), ("expr4:", expr4), ("expr5:", expr5), ("expr6:", expr6), ("expr7:", expr7),
    ("expr8:", expr8), ("expr9:", expr9), ("group:", group),
    ("object_instantiation:", object_instantiation), ("member_access",member_access),
    ("index_list:", index_list), ("index:", index), ("factor:", factor), ("type_simple:", type_simple),
    ("type_array:", type_array),("type_array_sized:", type_array_sized), ("type_func:", type_func),
    ("opt_param_list:", opt_param_list), ("param_list", param_list), ("param", param)
]

with open("railroad/Bminor++.html", "w", encoding="utf-8") as f:
    f.write("<html><head><title>Bminor++ Gramatica en diagrama</title><link rel='stylesheet' href='style.css'></head><body>")
    f.write("<div class='container'>")

    # Título
    f.write("<h1 class='main-title'>Gramática de Bminor++</h1>")
    f.write("<p class='subtitle'>Visualización de reglas mediante Diagramas de Ferrocarril</p>")
    
    for titulo, objeto_Diagrama in Diagramas:
        # Cada par de diagrama y titulo se seccionan en un div 'rule-group'
        f.write("<div class='rule-group'>")
        f.write(f"<h2>{titulo}</h2>")
        objeto_Diagrama.writeSvg(f.write)
        f.write("</div>") # Se cierra el grupo
        f.write("<hr>") 
        
    f.write("</div></body></html>")