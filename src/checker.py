from multimethod import multimeta, multimethod
from typing import Any, Optional
from dataclasses import dataclass
from symtab import Symtab
import typesys
from model import *

@dataclass
class Symbol:
	name: str
	kind: str          # var, param, func, class, array
	type: Any
	node: Any = None
	mutable: bool = True
	
	def __repr__(self):
		return f"Symbol(name={self.name!r}, kind={self.kind!r}, type={self.type!r})"

class Visitor(metaclass=multimeta):
    pass

class Checker(Visitor):
# -------------------------------------------------
# Inicialización del Checker
# -------------------------------------------------

    def __init__(self):
        self.errors = []
        self.symtab = Symtab("global")
        self.loopDepth = 0

# -------------------------------------------------
# Utilidades
# -------------------------------------------------

    def error(self, node, message: str):
        lineno = getattr(node, "lineno", "?")
        self.errors.append(f"Error: Linea {lineno}: {message}")
		
    def open_scope(self, name: str):
        if self.symtab is None:
            self.symtab = Symtab(name)
        else:
            self.symtab = Symtab(name, parent=self.symtab)
			
    def close_scope(self):
        if self.symtab is not None:
            self.symtab = self.symtab.parent
			
    def addSym(self, node, name: str, symbol: Symbol):
        try:
            self.symtab.add(name, symbol)
        except Symtab.SymbolDefinedError:
            self.error(node, f"redeclaración de '{name}' en el mismo alcance")
        except Symtab.SymbolConflictError:
            self.error(node, f"conflicto de símbolo '{name}'")
			
    def lookup(self, node, name: str):
        sym = self.symtab.get(name) if self.symtab else None
        if sym is None:
            self.error(node, f"símbolo '{name}' no definido")
        return sym
		
    def ok(self) -> bool:
        return len(self.errors) == 0
    
# -------------------------------------------------
# funciones de visita para cada nodo del AST
# -------------------------------------------------

    @multimethod
    def visit(self, node: Node):
        raise NotImplementedError(type(node).__name__)

    @multimethod
    def visit(self, node: Program):
        # visitamos cada nodo del programa
        for child_node in node.nodeList:
            self.visit(child_node)

    @multimethod
    def visit(self, node: SimpleDecl):
        if isinstance(node.dataType, Function):
            sym_kind = 'func'
            if isinstance(node.dataType.funcType, Array):
                sym_type = self.visit(node.dataType.funcType)
            else:
                sym_type = node.dataType.funcType
        elif isinstance(node.dataType, Array):
            sym_kind = 'array'
            sym_type = self.visit(node.dataType)
        else:
            sym_kind = 'var'
            sym_type = node.dataType

        sym = Symbol(name=node.varName, kind=sym_kind, type=sym_type, node=node)
        self.addSym(node, node.varName, sym)
        
    @multimethod
    def visit(self, node: InitDecl):
        # determinamos el tipo de simbolo y su tipo de datos
        if isinstance(node.dataType, Function):
            sym_kind = 'func'
            # determinamos si el tipo de dato es un array para obtener el tipo correcto
            if isinstance(node.dataType.funcType, Array):
                sym_type = self.visit(node.dataType.funcType)
            else:                   
                sym_type = node.dataType.funcType

        elif isinstance(node.dataType, Array):
            sym_kind = 'array'
            sym_type = self.visit(node.dataType)

        else:
            sym_kind = 'var'
            sym_type = node.dataType
        
        # agregamos el símbolo a la tabla de símbolos
        sym = Symbol(name=node.varName, kind=sym_kind, type=sym_type, node=node)
        self.addSym(node, node.varName, sym)

        # 1. para el caso de variables inicializadas que son funciones
        if sym.kind == 'func':

            # creamos un nuevo scope para el cuerpo de la funcion
            self.open_scope(f"function_{node.varName}")

            # guardamos el tipo de retorno declarado para la función en un atributo del checker 
            self.funcReturnType = sym.type
            # visitamos la cabecera de la función para registrar sus parámetros
            self.visit(node.dataType)
            # bandera para rastrear si encontramos un return dentro del cuerpo de la función
            self.hasReturned = False

            # visitamos el cuerpo de la función
            if node.value is not None:
                for stmt in node.value:
                    self.visit(stmt)

            if self.funcReturnType != 'void' and not self.hasReturned:
                self.error(node, f"La función '{node.varName}' no retorna ningún valor. Se esperaba un retorno de tipo '{self.funcReturnType}'.")

            # volvemos al scope padre
            self.close_scope()
            self.funcReturnType = None
        
        # 2. para el caso de variables inicializadas que son arreglos
        elif sym_kind == 'array':
            # visitamos el valor de inicialización del arreglo para verificar que los tipos conincidan
            if node.value is not None:
                for value in node.value:
                    valueType = self.visit(value)
                    if valueType != 'error' and valueType != sym_type:
                        self.error(node, f"Se esperaba un valor tipo '{sym_type}', pero se recibió un valor tipo '{valueType}' para el arreglo '{node.varName}'.")

        # 3. para el caso de variables inicializadas comunes
        else:
            if node.value is not None:
                valueType = self.visit(node.value)
                if valueType != 'error' and valueType != sym_type:
                    self.error(node, f"Se esperaba un valor tipo '{sym_type}', pero se recibió un valor tipo '{valueType}' para la variable '{node.varName}'.")

    @multimethod
    def visit(self, node: ClassDecl):
        # agregamos el simbolo al scope actual
        sym = Symbol(name=node.className, kind='class', type=node.className, node=node)
        self.addSym(node, node.className, sym)
        self.currentClass = node.className

        # creamos un nuevo scope para el cuerpo de la clase y lo guardamos en su simbolo
        self.open_scope(f"class_{node.className}")
        sym.inner_scope = self.symtab

        # visitamos su cuerpo
        if node.classBody is not None:
            for member in node.classBody:
                self.visit(member)

        # volvemos al scope padre
        self.close_scope()

    @multimethod
    def visit(self, node: If):
        # verificamos que la condición del if exista y sea de tipo booleano
        if node.condition is None:
            self.error(node, "La condición del 'if' no puede ser vacía.")
        else:
            conditionType = self.visit(node.condition)
            if conditionType != 'boolean' and conditionType != 'error':
                self.error(node, f"La condición del 'if' debe ser de tipo 'boolean', no '{conditionType}'.")

        # visitamos el nodo o nodos del cuerpo del if
        if node.ifBody is not None:
            self.visit(node.ifBody)

        # visitamos el nodo o nodos del cuerpo del else
        if node.elseBody is not None:
            self.visit(node.elseBody)

    @multimethod
    def visit(self, node: For):
        # aumentamos la profundidad de bucles para validar el uso de break/continue
        self.loopDepth += 1

        # visitamos la parte de inicialización del for
        if node.header[0] is not None:
            self.visit(node.header[0])
        
        # verificamos la parte de condición del for
        if node.header[1] is not None:
            conditionType = self.visit(node.header[1])
            if conditionType != 'boolean' and conditionType != 'error':
                self.error(node, f"La condición del 'for' debe ser de tipo 'boolean', no '{conditionType}'.")

        # verificamos la parte de actualización del for
        if node.header[2] is not None:
            self.visit(node.header[2])
    
        # vsitamos el nodo o nodos del cuerpo del for
        if node.forBody is not None:
            self.visit(node.forBody)
        
        # reducimos la profundidad de bucles
        self.loopDepth -= 1

    @multimethod
    def visit(self, node: While):
        # aumentamos la profundidad de bucles para validar el uso de break/continue
        self.loopDepth += 1

        # verificamos la condición del while
        if node.header is not None:
            conditionType = self.visit(node.header)
            if conditionType != 'boolean' and conditionType != 'error':
                self.error(node, f"La condición del 'while' debe ser de tipo 'boolean', no '{conditionType}'.")

        # visitamos el nodo o nodos del cuerpo del while
        if node.whileBody is not None:
            self.visit(node.whileBody)
        
        # reducimos la profundidad de bucles
        self.loopDepth -= 1

    @multimethod
    def visit(self, node: Print):
        # visitamos cada expresión a imprimir en caso de que haya una lista de expresiones
        for expr in node.value:
            self.visit(expr)

    @multimethod
    def visit(self, node: Return):
        # leemos el tipo de retorno declarado para la función actual
        funcReturnType = getattr(self, 'funcReturnType', None)
        
        # validamos que estemos realmente dentro de una función
        if funcReturnType is None:
            self.error(node, "Sentencia 'return' fuera del cuerpo de una función.")
            return 'error'

        self.hasReturned = True

        # si el valor de retorno es None, lo consideramos como 'void' para la comparación de tipos
        if node.value is None:
            valueType = 'void'
        else:
            valueType = self.visit(node.value)
        
        # verificamos que el tipo de retorno coincida con el declarado para la función
        if funcReturnType != valueType and valueType != 'error':
            self.error(node, f"La función/método espera retornar un valor de tipo '{funcReturnType}', pero se está retornando un valor de tipo '{valueType}'.")
        return valueType

    @multimethod
    def visit(self, node: Break):
        # validamos que la sentencia break esté dentro de un bucle
        if self.loopDepth == 0:
            self.error(node, "Sentencia 'break' fuera de un bucle.")

    @multimethod
    def visit(self, node: Continue):
        # validamos que la sentencia continue esté dentro de un bucle
        if self.loopDepth == 0:
            self.error(node, "Sentencia 'continue' fuera de un bucle.")

    @multimethod
    def visit(self, node: Block):
        # creamos un nuevo scope para el bloque
        self.open_scope(f"block_line_{node.lineno}")

        # visitamos cada sentencia en el bloque y volvemos al scope padre al terminar
        for stmt in node.stmtList:
            self.visit(stmt)
        
        self.close_scope()

    @multimethod
    def visit(self, node: Assignment):
        # visitamos el lado izquierdo y derecho de la asignación para obtener sus tipos
        leftType = self.visit(node.leftVal)
        rightType = self.visit(node.value)
        operator = node.operator

        # si alguno de los operandos ya produjo un error, propagamos el error y evitamos falsos positivos
        if leftType == 'error' or rightType == 'error':
            return 'error'

        # usamos el typesys para verificar que la operación de asignación sea válida entre tipos
        resultType = typesys.check_binop(operator, leftType, rightType)

        if resultType is None:
            self.error(node, f"Operación de asignación no válida entre tipos '{leftType}' y '{rightType}' con el operador '{operator}'.")
            return 'error'
        
        return resultType

    @multimethod
    def visit(self, node: TernaryOp):
        # verificamos que la condición del operador ternario exista y sea de tipo booleano
        if node.condition is None:
            self.error(node, "La condición del operador ternario no puede ser vacía.")
        else:
            conditionType = self.visit(node.condition)
            if conditionType != 'boolean' and conditionType != 'error':
                self.error(node, f"La condición del operador ternario debe ser de tipo 'boolean', no '{conditionType}'.")

        # visitamos las expresiones del cuerpo verdadero y falso del operador ternario
        if node.trueBody is None or node.falseBody is None:
            self.error(node, "Ambos cuerpos del operador ternario deben estar definidos.")
            return 'error'
        
        trueType = self.visit(node.trueBody)
        falseType = self.visit(node.falseBody)

        if trueType == 'error' or falseType == 'error':
            return 'error'

        # verificamos que los tipos de ambos cuerpos del operador ternario coincidan
        if trueType != falseType:
            self.error(node, f"Los tipos de los cuerpos del operador ternario deben coincidir ('{trueType}' vs '{falseType}').")
            return 'error'

        return trueType

    @multimethod
    def visit(self, node: Id):
        # buscamos el simbolo en los scopes
        symbol = self.lookup(node, node.name)
        if symbol is None:
            return 'error'  
            
        # retornamos su tipo de dato
        return symbol.type

    @multimethod
    def visit(self, node: IdIndex):
        # verificamos que el indice sea de tipo entero
        indexType = self.visit(node.index)
        if indexType != 'integer' and indexType != 'error':
            self.error(node, f"El índice de un arreglo debe ser de tipo 'integer', no '{indexType}'.")

        # obtenemos el símbolo del arreglo
        symbol = self.lookup(node, node.leftNode.name)
        if symbol is None:
            return 'error'

        # verificamos que el tipo del nodo izquierdo sea realmente un arreglo para poder indexarlo
        if symbol.kind != 'array':
            self.error(node, f"Solo se pueden indexar variables de tipo arreglo. '{node.leftNode.name}' fue declarada como '{symbol.kind}'.")
            return 'error'
        
        return symbol.type
        

    @multimethod
    def visit(self, node: GetAttr):
        # 1. verificamos el origen de llamada (this o un id)
        if node.varName == 'this':
            className = getattr(self, 'currentClass', None)
            if className is None:
                self.error(node, "Uso de 'this' fuera del contexto de una clase.")
                return 'error'
        else:
            # visitamos la variable para obtener su tipo (el mismo nombre de la clase)
            className = self.visit(node.varName)
            if className == 'error':
                return 'error'
            
        # 2. buscamos en la tabla de símbolos que esa clase realmente exista declarada
        symbol = self.lookup(node, className)
        if symbol is None:
            return 'error'
            
        if symbol.kind != 'class':
            self.error(node, f"El tipo '{className}' no es una clase y no se puede acceder a sus atributos.")
            return 'error'
        
        # 3. buscamos el scope de la clase para verificar que el atributo exista
        classScope = getattr(symbol, 'inner_scope', None)
        if classScope is None:
            self.error(node, f"No se encontró el entorno de la clase '{className}'.")
            return 'error'

        # 4. buscamos el símbolo del atributo dentro del scope de la clase
        attrSymbol = classScope.get(node.attr)
        if attrSymbol is None:
            self.error(node, f"La clase '{className}' no tiene un atributo llamado '{node.attr}'.")
            return 'error'
        
        return attrSymbol.type


    @multimethod
    def visit(self, node: BinaryOp):
        # visitamos el lado izquierdo y derecho de la operación para obtener sus tipos
        leftType = self.visit(node.leftVal)
        rightType = self.visit(node.rightVal)
        operator = node.operator

        if leftType == 'error' or rightType == 'error':
            return 'error'

        # usamos el typesys para verificar que la operación binaria sea válida entre tipos
        resultType = typesys.check_binop(operator, leftType, rightType)

        if resultType is None:
            self.error(node, f"Operación no válida entre tipos '{leftType}' y '{rightType}' con el operador '{operator}'.")
            return 'error'
        return resultType

    @multimethod
    def visit(self, node: UnaryOp):
        # visitamos el valor de la operación unaria para obtener su tipo
        valueType = self.visit(node.value)
        operator = node.operator

        # usamos el typesys para verificar que la operación unaria sea válida para el tipo
        resultType = typesys.check_unaryop(operator, valueType)

        if resultType is None:
            self.error(node, f"Operación unaria no válida para el tipo '{valueType}' con el operador '{operator}'.")
            return valueType
        return resultType

    @multimethod
    def visit(self, node: Call):
        # verificamos que la función a llamar realmente exista
        symbol = self.lookup(node, node.funcName)
        if symbol is None:
            return 'error'

        # verificamos que el símbolo encontrado sea realmente una función
        if symbol.kind != 'func':
            self.error(node, f"El identificador '{node.funcName}' no es una función y no se puede llamar.")
            return 'error'
        
        # verificamos que la cantidad de parámetros en la llamada coincida con la cantidad de parámetros declarados para la función
        funcParams = symbol.node.dataType.params
        callArgs = node.params

        if len(funcParams) != len(callArgs):
            self.error(node, f"La función '{node.funcName}' espera {len(funcParams)} parámetros, pero se le están pasando {len(callArgs)}.")
            return 'error'

        # verificamos que el tipo de cada argumento en la llamada coincida con el tipo declarado para cada parámetro de la función
        hay_errores = False
        for i, (paramFunc, argCall) in enumerate(zip(funcParams, callArgs)):
            # verificamos si el tipo declarado para el parámetro es un arreglo para obtener el tipo correcto a comparar con el argumento
            if isinstance(paramFunc.dataType, Array):
                paramType = self.visit(paramFunc.dataType)
            else:
                paramType = paramFunc.dataType

            argType = self.visit(argCall)

            if argType == 'error':
                hay_errores = True
                continue

            if paramType != argType:
                self.error(node, f"El parámetro {i+1} de la función '{node.funcName}' espera un valor de tipo '{paramType}', pero está recibiendo '{argType}'.")
                hay_errores = True
        
        if hay_errores:
            return 'error'
        
        return symbol.type

    @multimethod
    def visit(self, node: NewInstance):
        # verificamos que el tipo de clase a instanciar exista
        symbol = self.lookup(node, node.classType)
        if symbol is None:
            return 'error'
        
        # verificamos que el símbolo encontrado sea realmente una clase
        if symbol.kind != 'class':
            self.error(node, f"El identificador '{node.classType}' no es una clase y no se puede instanciar.")
            return 'error'

        # verficamos que la lista de parametros este vacia (por ahora no se soporta un constructor con parámetros)
        if node.params:
            self.error(node, f"La clase '{node.classType}' no tiene un constructor que acepte parámetros.")
            return 'error'
        
        return symbol.type


    @multimethod
    def visit(self, node: MethodCall):
        # verificamos que la clase del objeto al que se le quiere llamar el método exista
        className = self.visit(node.owner)
        if className == 'error':
            return 'error'
        
        # verificamos que el tipo encontrado para la clase sea realmente una clase para poder acceder a sus métodos
        symbol = self.lookup(node, className)
        if symbol is None:
            return 'error'
            
        if symbol.kind != 'class':
            self.error(node, f"El tipo '{className}' no es una clase y no se pueden llamar métodos de él.")
            return 'error'

        # buscamos el scope de la clase para verificar que el método exista
        classScope = getattr(symbol, 'inner_scope', None)
        if classScope is None:
            self.error(node, f"No se encontró el entorno de la clase '{className}'.")
            return 'error'
        
        methodSymbol = classScope.get(node.methodName)
        if methodSymbol is None:
            self.error(node, f"La clase '{className}' no tiene un método llamado '{node.methodName}'.")
            return 'error'

        if methodSymbol.kind != 'func':
            self.error(node, f"El atributo '{node.methodName}' de la clase '{className}' no es un método.")
            return 'error'
        
        # verificamos que la cantidad de parámetros en la llamada coincida con la cantidad de parámetros declarados para el método
        funcParams = methodSymbol.dataType.params
        callArgs = node.params

        if len(funcParams) != len(callArgs):
            self.error(node, f"El método '{node.methodName}' espera {len(funcParams)} parámetros, pero se le están pasando {len(callArgs)}.")
            return 'error'

        # verificamos que el tipo de cada argumento en la llamada coincida con el tipo declarado para cada parámetro del método
        hay_errores = False
        for i, (paramFunc, argCall) in enumerate(zip(funcParams, callArgs)):
            paramType = paramFunc.dataType
            argType = self.visit(argCall)

            if argType == 'error':
                hay_errores = True
                continue

            if paramType != argType:
                self.error(node, f"El parámetro {i+1} del método '{node.methodName}' espera un valor de tipo '{paramType}', pero está recibiendo '{argType}'.")
                hay_errores = True
        
        if hay_errores:
            return 'error'
        
        return methodSymbol.type

    @multimethod
    def visit(self, node: Literal):
        # retornamos el tipo de datos del literal según su categoría respecto al diccionario de tipos literales
        return self.LITERAL_TYPES.get(node.valueType, node.valueType)

    @multimethod
    def visit(self, node: Array):
        # verificamos que el tamaño del arreglo sea de tipo entero
        if node.size is not None:
            sizeType = self.visit(node.size)
            if sizeType != 'integer' and sizeType != 'error':
                self.error(node, f"El tamaño del arreglo debe ser de tipo 'integer', no '{sizeType}'.")
        
        # retornamos el tipo de datos del arreglo
        return node.valuesType

    @multimethod
    def visit(self, node: Function):
        # visitamos cada parametro de la función
        for param in node.params:
            self.visit(param)

    @multimethod
    def visit(self, node: ParamDecl):
        # si el parámetro es un arreglo, lo registramos como arreglo
        if isinstance(node.dataType, Array):
            sym_kind = 'array'
            sym_type = self.visit(node.dataType)
        else:
            sym_kind = 'param'
            sym_type = node.dataType
        
        sym = Symbol(name=node.varName, kind=sym_kind, type=sym_type, node=node)
        self.addSym(node, node.varName, sym)

    # diccionario para mapear los tipos de literales a sus correspondientes tipos de datos
    LITERAL_TYPES = {
        'INTEGER_LITERAL': 'integer',
        'FLOAT_LITERAL': 'float',
        'CHAR_LITERAL': 'char',
        'STRING_LITERAL': 'string',
        'BOOLEAN': 'boolean'
    }