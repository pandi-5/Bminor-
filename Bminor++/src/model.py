# model.pyyy

class Node:
    pass

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
    def __init__(self, className, value):
        self.className = className
        self.value = value

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

class Assignment(Node):
    def __init__(self, varName, operator, value):
        self.varName = varName
        self.operator = operator
        self.value = value

class TernaryOp(Node):
    def __init__(self, condition, ifBody, elseBody):
        self.condition = condition
        self.ifBody = ifBody
        self.elseBody = elseBody

class Id(Node):
    def __init__(self, name):
        self.name = name

class IdIndex(Node):
    def __init__(self, name, index):
        self.name = name
        self.index = index

class GetAttr(Node):
    def __init__(self, name, attr):
        self.name = name
        self.attr = attr

class BinaryOp(Node):
    def __init__(self, leftVal, operator, rightVal):
        self.left = leftVal
        self.operator = operator
        self.right = rightVal

class UnaryOp(Node):
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

class Call(Node):
    def __init__(self, funcName, args):
        self.funcName = funcName
        self.args = args    

class NewInstance(Node):
    def __init__(self, className, args):
        self.className = className
        self.args = args
    
class MethodCall(Node):
    def __init__(self, methodName, args):
        self.methodName = methodName
        self.args = args

class Literal(Node):
    def __init__(self, valueType, value):
        self.typeValue = valueType
        self.value = value

class Array(Node):
    def __init__(self, valuesType, size=None):
        self.typeValues = valuesType
        self.size = size

class Function(Node):
    def __init__(self, funcType, args):
        self.typeFunc = funcType
        self.args = args

class ParamDecl(Node):
    def __init__(self, varName, dataType):
        self.varName = varName
        self.dataType = dataType