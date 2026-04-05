# model.pyyy

class Node:
    def __repr__(self):
        # 1. Sacamos el nombre de tu clase (ej. 'InitDecl', 'BinaryOp')
        class_name = self.__class__.__name__
        
        # 2. Recorremos todo lo que guardaste en el __init__ y lo armamos bonito
        # (Ignoramos 'lineno' para que no ensucie mucho la pantalla, pero puedes quitar ese if si quieres verlo)
        atributos = []
        for llave, valor in self.__dict__.items():
            if llave != 'lineno':
                atributos.append(f"{llave}={repr(valor)}")
                
        # 3. Lo unimos todo en un texto estilo: InitDecl(varName='x', value=5)
        return f"{class_name}({', '.join(atributos)})"

class Program(Node):
    def __init__(self, nodeList):
        self.nodeList = nodeList

class SimpleDecl(Node):
    def __init__(self, varName, dataType):
        self.varName = varName
        self.dataType = dataType

class InitDecl(Node):
    def __init__(self, varName, dataType, value):
        self.varName = varName
        self.dataType = dataType
        self.value = value

class ClassDecl(Node):
    def __init__(self, className, classBody):
        self.className = className
        self.classBody = classBody

class If(Node):
    def __init__(self, condition, ifBody, elseBody):
        self.condition = condition
        self.ifBody = ifBody
        self.elseBody = elseBody

class For(Node):
    def __init__(self, header, forBody):
        self.header = header
        self.forBody = forBody

class While(Node):
    def __init__(self, header, whileBody):
        self.header = header
        self.whileBody = whileBody

class Print(Node):
    def __init__(self, value):
        self.value = value

class Return(Node):
    def __init__(self, value):
        self.value = value

class Break(Node):
    def __init__(self):
        pass

class Continue(Node):
    def __init__(self):
        pass

class Block(Node):
    def __init__(self, stmtList):
        self.stmtList = stmtList

class Assignment(Node):
    def __init__(self, leftVal, operator, value):
        self.leftVal = leftVal
        self.operator = operator
        self.value = value

class TernaryOp(Node):
    def __init__(self, condition, trueBody, falseBody):
        self.condition = condition
        self.trueBody = trueBody
        self.falseBody = falseBody

class Id(Node):
    def __init__(self, name):
        self.name = name

class IdIndex(Node):
    def __init__(self, leftNode, index):
        self.leftNode = leftNode
        self.index = index

class GetAttr(Node):
    def __init__(self, varName, attr):
        self.varName = varName
        self.attr = attr

class BinaryOp(Node):
    def __init__(self, leftVal, operator, rightVal):
        self.leftVal = leftVal
        self.operator = operator
        self.rightVal = rightVal

class UnaryOp(Node):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

class Call(Node):
    def __init__(self, funcName, params):
        self.funcName = funcName
        self.params = params    

class NewInstance(Node):
    def __init__(self, classType, params):
        self.classType = classType
        self.params = params

class MethodCall(Node):
    def __init__(self, owner, methodName, params):
        self.owner = owner
        self.methodName = methodName
        self.params = params

class Literal(Node):
    def __init__(self, valueType, value):
        self.valueType = valueType
        self.value = value

class Array(Node):
    def __init__(self, valuesType, size=None):
        self.valuesType = valuesType
        self.size = size

class Function(Node):
    def __init__(self, funcType, params):
        self.funcType = funcType
        self.params = params

class ParamDecl(Node):
    def __init__(self, varName, dataType):
        self.varName = varName
        self.dataType = dataType