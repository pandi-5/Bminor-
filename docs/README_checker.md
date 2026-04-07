# Analizador Semántico

Este proyecto implementa la fase de análisis semántico para el compilador. Se encarga de validar el significado del código fuente (AST) generado por el parser, verificando reglas de alcance (scope), compatibilidad de tipos y correcto uso de las estructuras de control.

## Cómo ejecutar el analizador semántico

Para ejecutar el analizador, debes pasar el archivo fuente como argumento al script principal :

```bash
python main.py archivo_de_prueba.txt
```

Al finalizar la ejecución, el programa imprimirá en consola cualquier error semántico encontrado indicando la línea exacta. Si no hay errores, el análisis concluye exitosamente.

---

## Implementación de la Tabla de Símbolos

La tabla de símbolos (`Symtab`) está diseñada para soportar **ámbitos anidados (Block Scoping)**. 

* **Estructura:** Se implementa como una estructura de datos que almacena el nombre de las variables y sus atributos (nodos de declaración).
* **Jerarquía de Scopes:** Cada tabla de símbolos tiene un puntero hacia su tabla padre (`parent`). Cuando se entra a un nuevo ámbito (como una función o un bloque de llaves `{}`), se crea una nueva instancia de `Symtab`.
* **Resolución de nombres:** Al buscar una variable, el sistema primero verifica el ámbito actual. Si no la encuentra, sigue recursivamente el puntero `parent` hacia los ámbitos superiores hasta llegar al global.
* **Ciclo de vida:** La creación y destrucción de los ámbitos intermedios está delegada al nodo `Block`, lo que unifica el manejo de memoria para funciones, condicionales (`if`), y ciclos (`while`, `for`).

---

## Implementación del Visitor con `@multimethod`

El recorrido del Árbol Sintáctico Abstracto (AST) se realiza utilizando el **Patrón Visitor**, potenciado por el decorador `@multimethod` de Python.

* **Sobrecarga de métodos:** En lugar de tener una función gigante con múltiples `if/elif` para verificar el tipo de nodo (`if isinstance(node, If): ...`), `@multimethod` permite definir múltiples métodos `visit()` en la misma clase, cada uno aceptando un tipo de nodo distinto (ej. `visit(self, node: If)`, `visit(self, node: BinaryOp)`).
* **Modularidad:** Esto hace que la lógica de cada nodo esté totalmente aislada.
* **Delegación:** Los nodos complejos (como las estructuras de control) delegan la validación de sus componentes internos visitando a sus nodos hijos directamente (`self.visit(hijo)`).

---

## Tipos de datos soportados por el sistema

El sistema de tipos (`typesys`) valida y soporta los siguientes tipos fundamentales:

* `integer`: Números enteros.
* `float`: Números de punto flotante.
* `boolean`: Valores lógicos (true/false).
* `char`: Caracteres individuales.
* `string`: Cadenas de texto.
* **Arreglos:** Tipos compuestos denotados por corchetes (ej. `arr : array [] integer`).
* **Funciones:** Validación de firmas (tipos de parámetros y tipo de retorno).
* `error`: Un tipo de dato interno utilizado para manejar silenciosamente fallos previos y evitar el "efecto dominó" (errores en cascada) en la consola.

---

## Chequeos Semánticos Implementados

El analizador realiza verificaciones exhaustivas en todo el AST:

1. **Declaración de variables:** Evita que se declare una variable dos veces en el mismo ámbito (lanzando `SymbolDefinedError`).
2. **Uso de variables no declaradas:** Verifica que cualquier identificador (`Id`) o arreglo referenciado exista en la tabla de símbolos actual o en las jerarquías superiores.
3. **Compatibilidad de Tipos (Operaciones):** Valida que las operaciones binarias (`BinaryOp`) y unarias ocurran entre tipos compatibles según las reglas del lenguaje.
4. **Condiciones Booleanas:** Exige que las condiciones en los nodos `If`, `While` y `For` se evalúen estrictamente como tipo `boolean`.
5. **Firmas de Funciones (Calls):** Verifica que la cantidad y los tipos de parámetros enviados en una llamada a función coincidan exactamente con la declaración de la función, incluyendo el paso de arreglos completos.
6. **Retornos de Función:** Valida que las sentencias `return` devuelvan el tipo de dato especificado en la firma de la función.
7. **Prevención de Errores en Cascada:** Implementación de retornos tempranos silenciosos (`'error'`) cuando un nodo hijo falla, para no inundar al usuario con falsos errores derivados de un mismo fallo.

---

## Aspectos Pendientes

* **Soporte de Constructores en Orientación a Objetos:** Falta la implementación de un método constructor para inicializar correctamente las instancias del sistema de orientación a objetos que fue agregado a la gramática original.
* **Cobertura de Pruebas en el Sistema de Clases:** Actualmente, el reporte y la propagación de errores semánticos dentro del ámbito de la orientación a objetos podrían presentar fallos o mensajes imprecisos. Esto se debe a la falta de tests exhaustivos específicos para esta nueva capa del lenguaje.
* Validar que todas las rutas de ejecución de una función terminen obligatoriamente en una instrucción `return` válida.