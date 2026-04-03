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

    @multimethod
    def visit(self, node: Node):
        raise NotImplementedError(type(node).__name__)

    @multimethod
    def visit(self, node: Program):
        for child_node in node.nodeList:
            self.visit(child_node)

    @multimethod
    def visit(self, node: SimpleDecl):
        try:
            self.symtab.add(node.varName, node)
        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.varName}' ya ha sido declarada.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para variable '{node.varName}'.")

    @multimethod
    def visit(self, node: InitDecl):
        try:
            # agrega la variable al scope global
            self.symtab.add(node.varName, node)

            # 1. si la variable es una función, creamos un nuevo scope para su cuerpo
            if isinstance(node.dataType, Function):
                scope_parent = self.symtab
                self.symtab = Symtab(node.varName, parent=scope_parent)
                self.funcReturnType = node.dataType.funcType
                # visitamos la función para procesar sus parámetros
                self.visit(node.dataType)
                # visitamos el cuerpo de la función (si es que tiene)
                if node.value is not None:
                    for stmt in node.value:
                        self.visit(stmt)
                # al terminar, volvemos al scope global
                self.symtab = scope_parent
                self.funcReturnType = None
            
            # 2. si la variable es un arreglo, verificamos que el tipo del valor coincida con el declarado
            elif isinstance(node.dataType, Array):
                dataTypeArray = self.visit(node.dataType)

                if node.value is not None:
                    for value in node.value:
                        valueType = self.visit(value)
                        if valueType != dataTypeArray:
                            self.errors.append(f"Error: Linea {node.lineno}: El valor y su tipo no coinciden para el arreglo '{node.varName}'.")

            # 3. en caso de ser una variable común, verificamos que el tipo del valor coincida con el declarado
            else:
                valueType = self.visit(node.value)
                if valueType != node.dataType:
                    self.errors.append(f"Error: Linea {node.lineno}: El valor y su tipo no coinciden para la variable '{node.varName}'.")

        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.varName}' ya ha sido declarada.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para variable '{node.varName}'.")

    @multimethod
    def visit(self, node: ClassDecl):
        try:
            self.symtab.add(node.className, node)
            # creamos un nuevo scope para el cuerpo de la clase
            scope_parent = self.symtab
            self.symtab = Symtab(node.className, parent=scope_parent)
            # visitamos el cuerpo de la clase
            for member in node.classBody:
                self.visit(member)
            # al terminar, volvemos al scope global
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
            if conditionType != 'boolean':
                self.errors.append(f"Error: Linea {node.lineno}: La condición del 'if' debe ser de tipo 'boolean', no '{conditionType}'.")

        # creamos un scope para el cuerpo del if y visitamos sus sentencias
        if node.ifBody is not None:
            scope_parent = self.symtab
            self.symtab = Symtab(f"if-block_line_{node.lineno}", parent=scope_parent)
            for stmt in node.ifBody:
                self.visit(stmt)
            self.symtab = scope_parent

        # creamos un scope para el cuerpo del else (si es que tiene) y visitamos sus sentencias
        if node.elseBody is not None:
            scope_parent = self.symtab
            self.symtab = Symtab(f"else-block_line_{node.lineno}", parent=scope_parent)
            for stmt in node.elseBody:
                self.visit(stmt)
            self.symtab = scope_parent

    @multimethod
    def visit(self, node: For):
        # visitamos la parte de inicialización del for (si es que tiene)
        if node.header[1] is not None:
            self.visit(node.header[1])
        
        # verificamos la parte de condición del for (si es que tiene)
        if node.header[2] is not None:
            conditionType = self.visit(node.header[2])
            if conditionType != 'boolean':
                self.errors.append(f"Error: Linea {node.lineno}: La condición del 'for' debe ser de tipo 'boolean', no '{conditionType}'.")

        # verificamos la parte de actualización del for (si es que tiene)
        if node.header[3] is not None:
            self.visit(node.header[3])
    
        # creamos un scope para el cuerpo del for y visitamos sus sentencias
        if node.forBody is not None:
            scope_parent = self.symtab
            self.symtab = Symtab(f"for-block_line_{node.lineno}", parent=scope_parent)
            for stmt in node.forBody:
                self.visit(stmt)
            self.symtab = scope_parent

    @multimethod
    def visit(self, node: While):
        pass

    @multimethod
    def visit(self, node: Print):
        pass

    @multimethod
    def visit(self, node: Return):
        # leemos el tipo de retorno declarado para la función actual (si es que estamos dentro de una función)
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
        if funcReturnType != valueType:
            self.errors.append(f"Error: Linea {node.lineno}: El tipo de retorno '{valueType}' no coincide con el declarado para la función ('{funcReturnType}').")
            
        return valueType



    @multimethod
    def visit(self, node: Break):
        pass

    @multimethod
    def visit(self, node: Continue):
        pass

    @multimethod
    def visit(self, node: Assignment):
        leftType = self.visit(node.leftVal)
        rightType = self.visit(node.value)
        operator = node.operator
        resultType = typesys.check_binop(operator, leftType, rightType)

        if resultType is None:
            self.errors.append(f"Error: Linea {node.lineno}: Operación de asignación no válida entre tipos '{leftType}' y '{rightType}' con el operador '{operator}'.")
            return leftType
        
        return resultType

    @multimethod
    def visit(self, node: TernaryOp):
        pass

    @multimethod
    def visit(self, node: Id):
        # leemos el símbolo de la variable en la tabla de símbolos
        symbol = self.symtab.get(node.name)        
        if symbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.name}' no ha sido declarada.")
            # tipo por defecto para evitar cascada de errores
            return 'integer'  
        else:
            # retornamos el tipo de datos de la variable
            return symbol.dataType

    @multimethod
    def visit(self, node: IdIndex):
        # verificamos que el indice sea de tipo entero
        indexType = self.visit(node.index)
        if indexType != 'integer':
            self.errors.append(f"Error: Linea {node.lineno}: El índice de un arreglo debe ser de tipo 'integer', no '{indexType}'.")

        # retornamos el tipo de datos que almacena el arreglo
        symbol = self.symtab.get(node.varName)
        if symbol is None:
            self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.varName}' no ha sido declarada.")
            return 'integer'
        else:
            if isinstance(symbol.dataType, Array):
                return symbol.dataType.valuesType
            else:
                self.errors.append(f"Error: Linea {node.lineno}: La variable '{node.varName}' no es un arreglo.")
                return 'integer'

    @multimethod
    def visit(self, node: GetAttr):
        pass

    @multimethod
    def visit(self, node: BinaryOp):
        leftType = self.visit(node.leftVal)
        rightType = self.visit(node.rightVal)
        operator = node.operator
        resultType = typesys.check_binop(operator, leftType, rightType)

        if resultType is None:
            self.errors.append(f"Error: Linea {node.lineno}: Operación no válida entre tipos '{leftType}' y '{rightType}' con el operador '{operator}'.")
            return leftType
        
        return resultType

    @multimethod
    def visit(self, node: UnaryOp):
        valueType = self.visit(node.value)
        operator = node.operator
        resultType = typesys.check_unaryop(operator, valueType)

        if resultType is None:
            self.errors.append(f"Error: Linea {node.lineno}: Operación unaria no válida para el tipo '{valueType}' con el operador '{operator}'.")
            return valueType
        
        return resultType

    @multimethod
    def visit(self, node: Call):
        pass

    @multimethod
    def visit(self, node: NewInstance):
        pass

    @multimethod
    def visit(self, node: MethodCall):
        pass

    @multimethod
    def visit(self, node: Literal):
        return self.LITERAL_TYPES.get(node.valueType, node.valueType)

    @multimethod
    def visit(self, node: Array):
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

    @multimethod
    def visit(self, node: ParamDecl):
        try:
            # agrega el parametro al scope de la funcion en caso de no estar declarado previamente
            self.symtab.add(node.varName, node)
        except Symtab.SymbolDefinedError:
            self.errors.append(f"Error: Linea {node.lineno}: El parámetro '{node.varName}' ya ha sido declarado en esta función.")
        except Symtab.SymbolConflictError:
            self.errors.append(f"Error: Linea {node.lineno}: Conflicto de tipos para parámetro '{node.varName}'.")

    LITERAL_TYPES = {
        'INTEGER_LITERAL': 'integer',
        'FLOAT_LITERAL': 'float',
        'CHAR_LITERAL': 'char',
        'STRING_LITERAL': 'string',
        'BOOLEAN': 'boolean'
    }