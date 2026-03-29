# Documentación Técnica: Analizador Léxico (Lexer) Bminor+

## 1. Introducción
El Analizador Léxico (Lexer) tiene como objetivo transformar el código fuente en una secuencia de **tokens** procesables. El sistema está construido bajo una arquitectura modular compuesta por:
* **Clase Lexer:** Núcleo de procesamiento basado en reglas de expresiones regulares.
* **Función `tokenize`:** Interfaz de generación y visualización de tokens.
* **Función `main`:** Punto de entrada para la ejecución mediante archivos externos.

---

## 2. Estructura de la Clase `Lexer`
Desarrollada utilizando las librerías **SLY** (Sly Lex-Yacc) para la lógica de tokenización y **Rich** para una salida visual formateada en consola.

### 2.1 Componentes Base (Preexistentes)
Se partió de una estructura inicial que incluía los siguientes elementos fundamentales:
* **Diccionario de Palabras Reservadas:** Conjunto de palabras clave de la gramática `bminor+` (ej. `if`, `else`, `while`, `for`, `return`) que el lexer identifica para evitar que sean tratadas como identificadores comunes.
* **Manejo de Identificadores:** Reglas básicas para diferenciar nombres de variables y funciones de las palabras clave.
* **Ignorancia de Espacios:** Procedimientos para omitir espacios en blanco, tabulaciones y retornos de carro.
* **Comentarios Estándar:** Expresiones regulares para ignorar comentarios de una sola línea (`//`) y comentarios de bloque debidamente cerrados (`/* ... */`).
* **Gestión de Errores Básica:** Una función `error` diseñada para capturar e informar sobre caracteres ilegales (símbolos no reconocidos por la gramática).

### 2.2 Implementaciones Nuevas y Mejoras
Se extendió la funcionalidad del Lexer para cumplir con las especificaciones detalladas de `bminor+`:
* **Literales de Datos:** Se diseñaron e implementaron expresiones regulares para:
    * **Enteros (`INTEGER_LITERAL`):** Números decimales.
    * **Flotantes (`FLOAT_LITERAL`):** Números con punto decimal.
    * **Caracteres (`CHAR_LITERAL`):** Soporte para caracteres individuales y secuencias de escape.
    * **Cadenas (`STRING_LITERAL`):** Manejo de texto entre comillas dobles con soporte para escapes.
* **Operadores de Relación:** Inclusión de tokens para comparaciones lógicas: `LT` (`<`), `GT` (`>`), `LE` (`<=`), `GE` (`>=`), `EQ` (`==`), `NE` (`!=`), entre otros.
* **Operadores de Asignación Compuesta:** Implementación de operadores como `ADDEQ` (`+=`), `SUBEQ` (`-=`), `MULEQ` (`*=`), `DIVEQ` (`/=`) y `MODEQ` (`%=`).
* **Control de Errores Avanzado:** Se añadieron dos manejadores de errores específicos para mejorar la experiencia del desarrollador:
    1.  **Error de Carácter sin cerrar:** Detecta cuando una declaración de tipo `char` no se cierra correctamente antes de un salto de línea o final de archivo.
    2.  **Error de Comentario de Bloque:** Identifica cuando un comentario iniciado con `/*` no encuentra su cierre `*/` antes del final del archivo, evitando la pérdida silenciosa de código y deteniendo la generación de tokens basura.



---

## 3. Funciones de Soporte

### 3.1 Función `tokenize(source)`
Esta función actúa como el puente entre el código crudo y la salida procesada.
* **Descripción:** Instancia la clase `Lexer` y recibe una cadena de texto (`source`). Itera sobre los tokens generados por el analizador y utiliza la librería `Rich` para imprimirlos de forma estructurada, permitiendo verificar el tipo de token, su valor y su posición (línea e índice).

### 3.2 Función `main` (Bloque de ejecución)
Es el punto de entrada principal del script cuando se ejecuta desde la línea de comandos.
* **Descripción:** Se encarga de la gestión de archivos. Verifica que el usuario haya proporcionado una ruta de archivo como argumento; si es así, abre el archivo con codificación UTF-8, lee su contenido y lo transfiere a la función `tokenize`. Incluye una validación de seguridad para asegurar que el programa solo se ejecute si se invoca directamente mediante el comando `python lexer.py`.

---

## 4. Diferencia entre Literales
Es importante destacar la distinción técnica implementada:
1.  **Símbolos Literales:** Representados en el código como caracteres únicos (`,`, `.`, `+`, `-`, `*`, `:`, entre otros), definidos directamente en la propiedad `literals` de la clase.
2.  **Tokens Literales:** Representaciones de valores de datos complejos (Enteros, Flotantes, Strings, Chars) que requieren expresiones regulares específicas para su validación y captura.

---


## 5. Implementación de Pruebas Unitarias (Pytest)

Para garantizar la fiabilidad del analizador léxico, se implementó una suite de pruebas automatizadas utilizando el framework **Pytest**. Estas pruebas validan tanto la correcta tokenización de elementos válidos como la capacidad de respuesta ante errores de sintaxis.

### 5.1 Estrategia de Pruebas por Categoría

Se diseñaron casos de prueba específicos para cubrir el espectro completo de la gramática:

* **Literales de Datos:** Se validaron casos borde para números (ej. `0`, `0.5`, `.5`), cadenas con secuencias de escape (ej. `"hola\n"`) y caracteres individuales.
* **Operadores y Palabras Reservadas:** Se verificó que combinaciones de símbolos (como `==`, `!=`, `+=`) se identifiquen como un único token y no como caracteres individuales separados.
* **Prioridad de Identificadores:** Pruebas para asegurar que palabras como `if` sean reconocidas como el token `IF` y no como un identificador de variable `ID`.



### 5.2 Pruebas de Control de Errores

Un aspecto crítico de la suite de pruebas es el uso del fixture `capsys` de Pytest, el cual permite capturar la salida de consola para validar los mensajes de error:

1.  **Caracteres Ilegales:** Se introducen símbolos fuera de la gramática (ej. `@`, `~`) y se verifica que la función `error()` reporte la línea y el carácter exacto.
2.  **Cierres Incompletos:** Se evalúa el comportamiento del Lexer ante comentarios (`/*`) y literales de carácter (`'`) que no son cerrados antes del final del archivo o línea, asegurando que se emita el aviso de error correspondiente y no se generen tokens basura.

### 5.3 Ejemplo de Estructura de Test

Las pruebas siguen el patrón **Arrange-Act-Assert**:
* **Arrange:** Definir la cadena de entrada (ej. `x = 10 + 5.5`).
* **Act:** Instanciar el Lexer y generar la lista de tokens.
* **Assert:** Comprobar que la cantidad de tokens es la esperada y que el `type` y `value` de cada uno coinciden con la especificación.

---