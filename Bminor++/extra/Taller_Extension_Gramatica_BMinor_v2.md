# Taller: Extensión de la Gramática de B-Minor (B-Minor+)

## Curso
Compiladores / Lenguajes de Programación

## Producto final del taller
El **producto final** que deben entregar los estudiantes es un **grafo de sintaxis (railroad diagrams)** de la gramática **B-Minor+**, generado con la librería **`railroad-diagrams` en Python**.

El resultado debe funcionar como un **atlas visual del lenguaje**, donde cada regla importante de la gramática tenga su propio diagrama.

---

## Objetivo general
Diseñar una **extensión del lenguaje B-Minor**, denominada **B-Minor+**, agregando nuevas construcciones **sin modificar la gramática original**, únicamente mediante **reglas adicionales** y nuevos no terminales.

---

## Restricción clave

> ⚠️ **No se permite modificar ninguna regla existente de la gramática base**.

Solo se permite:
- Agregar nuevos *tokens*
- Definir nuevos *non-terminals*
- Introducir nuevas alternativas que **compongan** la gramática original

---

## Extensiones a implementar

1. Definición de **clases y objetos**
2. Instrucción `while`
3. Operadores:
   - Incremento / decremento (`++`, `--`)
   - Asignación compuesta (`+=`, `-=`, `*=`, `/=`)
4. Operador condicional ternario `?:`

---

# Metodología del Taller

## Opción A (OBLIGATORIA): Diagramas curados

Los estudiantes deben **construir manualmente** los diagramas railroad a partir de la gramática, seleccionando reglas clave y justificando:

- precedencia
- asociatividad
- puntos de extensión del lenguaje

❌ No se permite generación automática directa desde la BNF.

### Reglas mínimas a diagramar

**Statements**
- stmt
- open_stmt / closed_stmt
- if_stmt_open / if_stmt_closed
- for_stmt_open / for_stmt_closed
- while_stmt_open / while_stmt_closed
- simple_stmt

**Expressions**
- niveles de precedencia (`expr1` … `expr9`) o versión transformada
- operadores `+=`, `-=`, `*=`, `/=`
- pre y post `++`, `--`
- operador ternario `?:`

**Clases y Objetos**
- class_decl
- class_body
- class_member
- creación con `new`
- acceso a miembros `.`

---

## Opción B (BONUS): Generación semi-automática

Implementar una herramienta que:

1. Lea reglas simples desde la gramática (`.bnf` / `.ebnf`)
2. Genere diagramas automáticamente **solo para reglas no recursivas**
3. Permita intervención manual para reglas complejas

### Reglas excluidas del bonus automático
- Expresiones con recursión izquierda
- Reglas de precedencia

Ejemplo de transformación conceptual:

```bnf
expr5 ::= expr5 '+' expr6 | expr6
```

→

```bnf
expr5 ::= expr6 (('+' | '-') expr6)*
```

---

## Herramienta: railroad-diagrams (Python)

### Instalación

```bash
pip install railroad-diagrams
```

### Ejemplo mínimo

```python
from railroad import Diagram, Sequence, Choice, Terminal, NonTerminal

def T(x): return Terminal(x)
def N(x): return NonTerminal(x)

def d_while_stmt_closed():
    return Diagram(
        Sequence(
            T("WHILE"),
            T("("),
            N("opt_expr"),
            T(")"),
            N("closed_stmt")
        )
    )
```

---

## Salida esperada

- Diagramas en formato **SVG**
- Carpeta `out/svg/`
- Archivo `out/index.md` que incruste los diagramas (compatible con Obsidian)

Ejemplo:

```markdown
## Statements
![[svg/stmt.svg]]
![[svg/while_stmt_closed.svg]]
```

---

## Rúbrica de evaluación

| Criterio | Porcentaje |
|--------|------------|
| Diagramas correctos y completos | 40% |
| Precedencia y asociatividad | 25% |
| Organización y claridad del atlas | 20% |
| Reproducibilidad del proyecto | 15% |
| **Bonus B** | +10% |

---

## Resultados de aprendizaje

Al finalizar el taller, el estudiante será capaz de:
- Leer y comprender gramáticas reales
- Extender un lenguaje sin romper compatibilidad
- Representar sintaxis formal visualmente
- Comprender precedencia y asociatividad
- Conectar BNF → AST → Parser → Diagramas

---
