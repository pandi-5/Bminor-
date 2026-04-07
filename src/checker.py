from multimethod import multimeta, multimethod
from symtab import Symtab
import typesys
from model import *

class Visitor(metaclass=multimeta):
    pass

class Checker(Visitor):
    def __init__(self):
        self.errors = []
        self.symtab = Symtab("global")
        self.loopDepth = 0

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
        try:
            # agrega la variable al scope actual
            self.symtab.add(node.varName, node)
        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.varName}' ya ha sido declarada.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para variable '{node.varName}'.")

    @multimethod
    def visit(self, node: InitDecl):
        try:
            # agrega la variable al scope actual
            self.symtab.add(node.varName, node)

            # 1. si la variable es una función, creamos un nuevo scope para su cuerpo
            if isinstance(node.dataType, Function):
                scope_parent = self.symtab
                self.symtab = Symtab(node.varName, parent=scope_parent)

                # visitamos la cabecera de la función para registrar sus parámetros y obtener su tipo de retorno
                self.funcReturnType = self.visit(node.dataType)

                # visitamos el cuerpo de la función (si es que tiene)
                if node.value is not None:
                    for stmt in node.value:
                        self.visit(stmt)

                # al terminar, volvemos al scope padre
                self.symtab = scope_parent
                self.funcReturnType = None
            
            # 2. si la variable es un arreglo, verificamos que el tipo del valor coincida con el declarado
            elif isinstance(node.dataType, Array):
                dataTypeArray = self.visit(node.dataType)

                if node.value is not None:
                    for value in node.value:
                        valueType = self.visit(value)
                        if valueType != 'error' and valueType != dataTypeArray:
                            self.errors.append(f"Error: Linea {node.lineno}: Se esperaba un valor tipo '{dataTypeArray}', pero se recibió un valor tipo '{valueType}' para el arreglo '{node.varName}'.")

            # 3. en caso de ser una variable común, verificamos que el tipo del valor coincida con el declarado
            else:
                valueType = self.visit(node.value)
                if valueType != 'error' and valueType != node.dataType:
                    self.errors.append(f"Error: Linea {node.lineno}: Se esperaba un valor tipo '{node.dataType}', pero se recibió un valor tipo '{valueType}' para la variable '{node.varName}'.")

        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.varName}' ya ha sido declarada.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para variable '{node.varName}'.")

    @multimethod
    def visit(self, node: ClassDecl):
        try:
            # agregamos la clase al scope actual y creamos un nuevo scope para su cuerpo
            self.symtab.add(node.className, node)
            scope_parent = self.symtab
            self.currentClass = node.className
            self.symtab = Symtab(node.className, parent=scope_parent)

            # visitamos el cuerpo de la clase
            for member in node.classBody:
                self.visit(member)

            # al terminar, volvemos al scope padre
            self.symtab = scope_parent
        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{node.className}' ya ha sido declarada.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para clase '{node.className}'.")

    @multimethod
    def visit(self, node: If):
        # verificamos que la condición del if exista y sea de tipo booleano
        if node.condition is None:
            self.errors.append(f"Error: Linea {node.lineno}: La condición del 'if' no puede ser vacía.")
        else:
            conditionType = self.visit(node.condition)
            if conditionType != 'boolean' and conditionType != 'error':
                self.errors.append(f"Error: Linea {node.lineno}: La condición del 'if' debe ser de tipo 'boolean', no '{conditionType}'.")

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

        # visitamos la parte de inicialización del for (si es que tiene)
        if node.header[0] is not None:
            self.visit(node.header[0])
        
        # verificamos la parte de condición del for (si es que tiene)
        if node.header[1] is not None:
            conditionType = self.visit(node.header[1])
            if conditionType != 'boolean' and conditionType != 'error':
                self.errors.append(f"Error: Linea {node.lineno}: La condición del 'for' debe ser de tipo 'boolean', no '{conditionType}'.")

        # verificamos la parte de actualización del for (si es que tiene)
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
                self.errors.append(f"Error: Linea {node.lineno}: La condición del 'while' debe ser de tipo 'boolean', no '{conditionType}'.")

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
            self.errors.append(f"Error: Linea {node.lineno}: Sentencia 'return' fuera del cuerpo de una función.")
            return 'void'

        # si el valor de retorno es None, lo consideramos como 'void' para la comparación de tipos
        if node.value is None:
            valueType = 'void'
        else:
            valueType = self.visit(node.value)
        
        # verificamos que el tipo de retorno coincida con el declarado para la función
        if funcReturnType != valueType and valueType != 'error':
            self.errors.append(f"Error: Linea {node.lineno}: La funcion/metodo espera retornar un valor de tipo '{funcReturnType}', pero se está retornando un valor de tipo '{valueType}'.")
        return valueType

    @multimethod
    def visit(self, node: Break):
        # validamos que la sentencia break esté dentro de un bucle
        if self.loopDepth == 0:
            self.errors.append(f"Error: Linea {node.lineno}: Sentencia 'break' fuera de un bucle.")

    @multimethod
    def visit(self, node: Continue):
        # validamos que la sentencia continue esté dentro de un bucle
        if self.loopDepth == 0:
            self.errors.append(f"Error: Linea {node.lineno}: Sentencia 'continue' fuera de un bucle.")

    @multimethod
    def visit(self, node: Block):
        # creamos un nuevo scope para el bloque
        scopeParent = self.symtab
        self.symtab = Symtab(f"block_line_{node.lineno}", parent=scopeParent)

        # visitamos cada sentencia en el bloque y volvemos al scope padre al terminar
        for stmt in node.stmtList:
            self.visit(stmt)
        
        self.symtab = scopeParent

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
            self.errors.append(f"Error: Linea {node.lineno}: Operación de asignación no válida entre tipos '{leftType}' y '{rightType}' con el operador '{operator}'.")
            return 'error'
        
        return resultType

    @multimethod
    def visit(self, node: TernaryOp):
        # verificamos que la condición del operador ternario exista y sea de tipo booleano
        if node.condition is None:
            self.errors.append(f"Error: Linea {node.lineno}: La condición del operador ternario no puede ser vacía.")
        else:
            conditionType = self.visit(node.condition)
            if conditionType != 'boolean':
                self.errors.append(f"Error: Linea {node.lineno}: La condición del operador ternario debe ser de tipo 'boolean', no '{conditionType}'.")

        # visitamos las expresiones del cuerpo verdadero y falso del operador ternario
        if node.trueBody is None or node.falseBody is None:
            self.errors.append(f"Error: Linea {node.lineno}: Ambos cuerpos del operador ternario deben estar definidos.")
            return 'error'
        
        trueType = self.visit(node.trueBody)
        falseType = self.visit(node.falseBody)

        # verificamos que los tipos de ambos cuerpos del operador ternario coincidan
        if trueType != falseType:
            self.errors.append(f"Error: Linea {node.lineno}: Los tipos de los cuerpos del operador ternario deben coincidir ('{trueType}' vs '{falseType}').")
            return trueType

        return trueType

    @multimethod
    def visit(self, node: Id):
        # leemos el símbolo de la variable en la tabla de símbolos
        symbol = self.symtab.get(node.name)        
        if symbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.name}' no ha sido declarada.")
            return 'error'  
        else:
            if isinstance(symbol.dataType, Array):
                # si el símbolo es un arreglo, retornamos el tipo de datos que almacena el arreglo
                return self.visit(symbol.dataType)
            
            # en caso contrario, retornamos el tipo de datos del símbolo
            return symbol.dataType

    @multimethod
    def visit(self, node: IdIndex):
        # verificamos que el indice sea de tipo entero
        indexType = self.visit(node.index)
        if indexType != 'integer':
            self.errors.append(f"Error: Linea {node.lineno}: El índice de un arreglo debe ser de tipo 'integer', no '{indexType}'.")

        # obtenemos el símbolo del arreglo
        symbol = self.symtab.get(node.leftNode.name)
        if symbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.leftNode.name}' no ha sido declarada.")
            return 'error'
        arrayType = symbol.dataType

        # verificamos que el tipo del nodo izquierdo sea realmente un arreglo para poder indexarlo
        if not isinstance(arrayType, Array):
            self.errors.append(f"Error: Linea {node.lineno}: Solo se pueden indexar variables de tipo arreglo, no '{arrayType}'.")
            return 'error'
        else:
            # retornamos el tipo de datos que almacena el arreglo
            return arrayType.valuesType
        

    @multimethod
    def visit(self, node: GetAttr):
        # 1. verificamos el acceso a atributo a travez de this
        if node.varName == 'this':
            className = getattr(self, 'currentClass', None)
            if className is None:
                self.errors.append(f"Error: Linea {node.lineno}: Uso de 'this' fuera del contexto de una clase.")
                return 'error'
        # 2. verificamos el acceso a atributos de otras variables
        else:
            varType = self.visit(node.varName)
            if varType == 'error':
                return 'error'
            # buscamos el tipo de la variable para verificar que sea una clase y poder acceder a sus atributos
            typeSymbol = self.symtab.get(varType)
            if not isinstance(typeSymbol, ClassDecl):
                self.errors.append(f"Error: Linea {node.lineno}: El tipo '{varType}' no es una clase y no se puede acceder a sus atributos.")
                return 'error'
            
            className = varType
        
        # 3. buscamos el scope de la clase para verificar que el atributo exista
        classScope = next((child for child in self.symtab.children if child.name == className), None)
        if classScope is None:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{className}' no ha sido declarada.")
            return 'error'

        # 4. buscamos el símbolo del atributo dentro del scope de la clase
        attrSymbol = classScope.get(node.attr)
        if attrSymbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{className}' no tiene un atributo llamado '{node.attr}'.")
            return 'error'
        return attrSymbol.dataType


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
            self.errors.append(f"Error: Linea {node.lineno}: Operación no válida entre tipos '{leftType}' y '{rightType}' con el operador '{operator}'.")
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
            self.errors.append(f"Error: Linea {node.lineno}: Operación unaria no válida para el tipo '{valueType}' con el operador '{operator}'.")
            return valueType
        return resultType

    @multimethod
    def visit(self, node: Call):
        # verificamos que la función a llamar realmente exista
        funcSymbol = self.symtab.get(node.funcName)
        if funcSymbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La función '{node.funcName}' no ha sido declarada.")
            return 'error'

        # verificamos que el símbolo encontrado sea realmente una función
        if not isinstance(funcSymbol.dataType, Function):
            self.errors.append(f"Error: Linea {node.lineno}: El símbolo '{node.funcName}' no es una función y no se puede llamar.")
            return 'error'
        
        # verificamos que la cantidad de parámetros en la llamada coincida con la cantidad de parámetros declarados para la función
        func = funcSymbol.dataType.params
        call = node.params

        if len(func) != len(call):
            self.errors.append(f"Error: Linea {node.lineno}: La función '{node.funcName}' espera {len(func)} parámetros, pero se le están pasando {len(call)}.")
            return 'error'

        # verificamos que el tipo de cada argumento en la llamada coincida con el tipo declarado para cada parámetro de la función
        hay_errores = False
        for i, (paramFunc, paramCall) in enumerate(zip(func, call)):
            # verificamos si el tipo declarado para el parámetro es un arreglo para obtener el tipo correcto a comparar con el argumento
            if isinstance(paramFunc.dataType, Array):
                paramType = self.visit(paramFunc.dataType)
            else:
                paramType = paramFunc.dataType

            argType = self.visit(paramCall)

            if argType == 'error':
                continue

            if paramType != argType:
                self.errors.append(f"Error: Linea {node.lineno}: El parámetro {i+1} de la función '{node.funcName}' espera un valor de tipo '{paramType}', pero esta recibiendo un valor de tipo '{argType}'.")
                hay_errores = True
        
        if hay_errores:
            return 'error'
        
        return funcSymbol.dataType.funcType

    @multimethod
    def visit(self, node: NewInstance):
        # verificamos que el tipo de clase a instanciar exista
        classSymbol = self.symtab.get(node.classType)
        if classSymbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{node.classType}' no ha sido declarada.")
            return 'error'
        
        # verificamos que el símbolo encontrado sea realmente una clase
        if not isinstance(classSymbol, ClassDecl):
            self.errors.append(f"Error: Linea {node.lineno}: El tipo '{node.classType}' no es una clase y no se puede instanciar.")
            return 'error'

        # verficamos que la lista de parametros este vacia (por ahora no se soporta un constructor con parámetros)
        if node.params:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{node.classType}' no tiene un constructor que acepte parámetros.")
            return 'error'
        return node.classType


    @multimethod
    def visit(self, node: MethodCall):
        # verificamos que la clase del objeto al que se le quiere llamar el método exista
        className = self.visit(node.owner)
        if className == 'error':
            return 'error'
        
        # verificamos que el tipo encontrado para la clase sea realmente una clase para poder acceder a sus métodos
        typeSymbol = self.symtab.get(className)
        if not isinstance(typeSymbol, ClassDecl):
            self.errors.append(f"Error: Linea {node.lineno}: El tipo '{className}' no es una clase y no se pueden llamar métodos de él.")
            return 'error'

        # buscamos el scope de la clase para verificar que el método exista
        classScope = next((child for child in self.symtab.children if child.name == className), None)
        if classScope is None:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{className}' no ha sido declarada.")
            return 'error'
        
        methodSymbol = classScope.get(node.methodName)
        if methodSymbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La clase '{className}' no tiene un método llamado '{node.methodName}'.")
            return 'error'
        
        # verificamos que la cantidad de parámetros en la llamada coincida con la cantidad de parámetros declarados para el método
        func = methodSymbol.dataType.params
        call = node.params

        if len(func) != len(call):
            self.errors.append(f"Error: Linea {node.lineno}: El método '{node.methodName}' espera {len(func)} parámetros, pero se le están pasando {len(call)}.")
            return 'error'

        # verificamos que el tipo de cada argumento en la llamada coincida con el tipo declarado para cada parámetro del método
        hay_errores = False
        for i, (paramFunc, paramCall) in enumerate(zip(func, call)):
            paramType = paramFunc.dataType
            argType = self.visit(paramCall)

            if argType == 'error':
                continue

            if paramType != argType:
                self.errors.append(f"Error: Linea {node.lineno}: El parámetro {i+1} del método '{node.methodName}' espera un valor de tipo '{paramType}', pero esta recibiendo un valor de tipo '{argType}'.")
                hay_errores = True
        
        if hay_errores:
            return 'error'
        
        return methodSymbol.dataType.funcType

    @multimethod
    def visit(self, node: Literal):
        # retornamos el tipo de datos del literal según su categoría respecto al diccionario de tipos literales
        return self.LITERAL_TYPES.get(node.valueType, node.valueType)

    @multimethod
    def visit(self, node: Array):
        # verificamos que el tamaño del arreglo (si es que tiene) sea de tipo entero
        if node.size is not None:
            sizeType = self.visit(node.size)
            if sizeType != 'integer':
                self.errors.append(f"Error: Linea {node.lineno}: El tamaño del arreglo debe ser de tipo 'integer', no '{sizeType}'.")
                
        # retornamos el tipo de datos que almacena el arreglo
        return node.valuesType
        

    @multimethod
    def visit(self, node: Function):
        # visitamos cada parametro de la función (si es que tiene)
        for param in node.params:
            self.visit(param)

        # verificamos si el tipo de retorno es simple o un arreglo para retornar el tipo correcto de la función
        if isinstance(node.funcType, Array):
            return self.visit(node.funcType)
        else:
            return node.funcType

    @multimethod
    def visit(self, node: ParamDecl):
        try:
            # agrega el parametro al scope de la funcion en caso de no estar declarado previamente
            self.symtab.add(node.varName, node)
        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: El parámetro '{node.varName}' ya ha sido declarado en esta función.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para parámetro '{node.varName}'.")

    # diccionario para mapear los tipos de literales a sus correspondientes tipos de datos
    LITERAL_TYPES = {
        'INTEGER_LITERAL': 'integer',
        'FLOAT_LITERAL': 'float',
        'CHAR_LITERAL': 'char',
        'STRING_LITERAL': 'string',
        'BOOLEAN': 'boolean'
    }