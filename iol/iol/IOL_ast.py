from enum import Enum

# class to handle whole program 
class ProgramNode:
    def __init__(self, statements):
        self.statements = statements

    # returns a list of all visited nodes
    def visit(self):
        visited = []
        for statement in self.statements:
            visited.append(statement.visit())

        return visited

# class to handle a single statement of the program
class StatementNode:
    def __init__(self, statement, line_num):
        self.statement = statement
        self.line_num = line_num

    def visit(self):
        return self.statement.visit()

# Statement Nodes
# class to handle variable declaration statemenents
class VariableDeclarationNode:
    def __init__(self, data_type, var_name, line_num, expression=None):
        self.data_type = data_type
        self.var_name = var_name
        self.expression = expression
        self.line_num = line_num

    def visit(self):
        if self.expression != None:
            # return self with visited expression node
            return VariableDeclarationNode(self.data_type, self.var_name, self.line_num, self.expression.visit())
        else:
            return self


# class to handle variable assignment statements
class AssignmentNode:
    def __init__(self, var_name, expression, line_num):
        self.var_name = var_name
        self.expression= expression
        self.line_num = line_num

    def visit(self):
        # return self with visited expression node
        return AssignmentNode(self.var_name, self.expression.visit(), self.line_num)

# class to handle input statements
class InputNode:
    def __init__(self, var_name, line_num):
        self.var_name = var_name
        self.line_num = line_num

    def visit(self):
        return self

# class to handle output statements
class OutputNode:
    def __init__(self, expression, line_num):
        self.expression = expression
        self.line_num = line_num

    def visit(self):
        # return self with visited expression node
        return OutputNode(self.expression.visit(), self.line_num)

# End of Statement Nodes

# class to handle the expression of the statements
class ExpressionNode:
    def __init__(self, expression, line_num):
        self.expression = expression
        self.line_num = line_num

    def visit(self):
        # return self with visited expression node
        return self.expression.visit()

# Expression Nodes

# class to handle binary operations
class BinaryExpressionNode:
    def __init__(self, operation, left, right, line_num):
        self.operation = operation
        self.left = left
        self.right = right
        self.line_num = line_num

    def visit(self):
        # return self with visited left and right nodes
        return BinaryExpressionNode(self.operation, self.left.visit(), self.right.visit(), self.line_num)

    # returns a list of all operands associated with the operation
    def getInner(self):
        left = [item for item in self.left.getInner()]
        right = [item for item in self.right.getInner()]
        return left+right


# class to handle operands of the expressions
class OperandNode:
    def __init__(self, operand, line_num):
        self.operand = operand
        self.line_num = line_num

    def visit(self):
        # returns self with visited operand node
        return self.operand.visit()

# End of Expression Nodes

# class to handle numeric literals in a statement
class NumericLiteralNode:
    def __init__(self, value, line_num):
        self.value = value
        self.line_num = line_num

    def visit(self):
        return self

    def getInner(self):
        # returns the value of the node as a list
        return [self.value]

# class to handle identifiers/variables in a statement
class IdentifierNode:
    def __init__(self, var_name, line_num):
        self.var_name = var_name
        self.line_num = line_num

    def visit(self):
        return self

    def getInner(self):
        # returns the identifier/variable name associated with the node as a list
        return [self.var_name]


# class to handle newline statements
class NewlineNode:
    def __init__(self, line_num):
        self.line_num = line_num

    def visit(self):
        return self    


# Error Node -> class to handle error nodes determined by the parser
class ErrorNode:
    def __init__(self, value, line_num):
        self.value = value
        self.line_num = line_num

    def visit(self):
        return self
