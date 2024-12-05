from IOL_lexer import *
from IOL_ast import *
from IOL_parser import *
from IOL_executor import *
'''
 allows for semantic analysis of a given abstract tree representation of a source file
 it checks for the following:
    1. multiple declarations of a variable
    2. incompatible data types in assignment and declarations statements*
    3. incompatible types in arithmetic/binary operations*
    4. use of undeclared variables (checked thorugh symbol table)
 *if encountered, it replaces the node into an error node

 also assigns intial value to variables defined without initial value
    for INT it assigns 0, empty string for STR 
'''
class SemanticAnalyzer():
    def __init__(self, ast, symbol_table):
        self.ast = ast
        self.symbol_table = symbol_table
        self.errors = []

        self.checkMultipleDeclarations()
        self.checkDeclarationAssignements()
        self.checkAssignmentOperations()
        self.checkBinaryOperations()

        self.assignVariables()
        self.checkUndeclaredVariables()

    # checks for variables that are declared more than once
    def checkMultipleDeclarations(self):
        # visit all VariableDeclarationNodes
        node = [ item for item in self.ast.visit() if type(item) == VariableDeclarationNode]
        
        skip = []
        # check for double declaration, same ident and same/different data type
        for item in node:
            count = 0
            line = []
            for decl in node:
                if decl.var_name == item.var_name:
                    count += 1
                    line.append(decl.line_num)

            # variable is declared more than once
            if count > 1 and item.var_name not in skip:
                lines = ', '.join(str(x) for x in line[1:])
                self.errors.append(f'Conflicting declaration(s) of \'{item.var_name}\' at line(s) {lines}')
                skip.append(item.var_name)

    # checks for incompatible assignment in variable declaration statements
    # if incompatible, it changes the VariableDeclarationNode into ErrorNode
    # appends semantic errors found while processing
    def checkDeclarationAssignements(self):
        # visit all VariableDeclarationNodes
        nodes = self.ast.visit()
        nodes = [ item for item in self.ast.visit() if type(item) == VariableDeclarationNode]

        for node in nodes:
            if node.expression == None:
                continue

            name = node.var_name
            data_type = node.data_type
            temp = node
            error = False

            if type(temp.expression.visit()) == BinaryExpressionNode:
                # STR var → BinaryOp
                if data_type != TOKEN.INT:
                    error = True
                    err = f'Incompatible data types at assignment operation in \'{name}\' declaration at line {node.line_num}'
                    self.errors.append(err)

            elif type(temp.expression.visit()) == NumericLiteralNode:
                # STR → numeric literal
                if data_type != TOKEN.INT:
                    print(data_type, TOKEN.INT)
                    error = True
                    err = f'Incompatible data types at assignment operation in \'{name}\' declaration at line {node.line_num}'
                    self.errors.append(err)

            elif type(temp.expression.visit()) == IdentifierNode:
                # INT → STR or STR → INT
                if data_type != self.symbol_table[temp.expression.visit().var_name]['type']:
                    print(data_type, self.symbol_table[temp.expression.visit().var_name]['type'])
                    error = True
                    err = f'Incompatible data types at assignment operation for \'{name}\' declaration at line {node.line_num}'
                    self.errors.append(err)

            # replace current ndoe to error node
            if error:
                new_node = ErrorNode("Incompatible data types at declaration statement", node.line_num)
                self.ast.statements = [new_node if statement == node else statement for statement in self.ast.statements]

    # checks for incompatible data types in asssignment statements
    # if incompatible, it changes the AssignmentNode into ErrorNode
    # appends semantic errors found while processing
    def checkAssignmentOperations(self):
        nodes = self.ast.visit()
        nodes = [ item for item in nodes if type(item) == AssignmentNode]

        for node in nodes:
            name = node.var_name
            data_type = self.symbol_table[node.var_name]['type']
            temp = node
            error = False

            if type(temp.expression.visit()) == BinaryExpressionNode:
                # STR var → BinaryOp
                if data_type != TOKEN.INT.value:
                    error = True
                    err = f'Incompatible data types for assignment operation for \'{name}\' at line {node.line_num}'
                    self.errors.append(err)

            elif type(temp.expression.visit()) == NumericLiteralNode:
                # STR → numeric literal
                if data_type != TOKEN.INT.value:
                    error = True
                    err = f'Incompatible data types for assignment operation for \'{name}\' at line {node.line_num}'
                    self.errors.append(err)

            elif type(temp.expression.visit()) == IdentifierNode:
                # INT → STR or STR → INT
                if data_type != self.symbol_table[temp.expression.visit().var_name]['type']:
                    error = True
                    err = f'Incompatible data types for assignment operation for \'{name}\' at line {node.line_num}'
                    self.errors.append(err)

            # replace current node to error node
            if error:
                new_node = ErrorNode("Incompatible data types at assignement operation", node.line_num)
                self.ast.statements = [new_node if statement == node else statement for statement in self.ast.statements]

    # checks for incompatible data types of operand for all arithemtic/binary operations by visisting all binary expressions
    # if incompatible, it changes the VariableDeclarationNode into ErrorNode
    # appends semantic errors found while processing
    def checkBinaryOperations(self):
        nodes = self.ast.visit()
        # ignore these nodes
        leaf_nodes = [NewlineNode, IdentifierNode, NumericLiteralNode, InputNode, ErrorNode]

        # remove leaf nodes in node list
        nodes = [item for item in nodes if type(item) not in leaf_nodes]
        
        # collate all BinaryExpressionNode
        while True:
            temp = []
            for node in nodes:
                if type(node) != BinaryExpressionNode:
                    # remove if expression is None in the declaration node
                    if type(node) == VariableDeclarationNode and node.expression == None:
                        continue
                    elif type(node) == ExpressionNode:
                        temp.append(item.visit())
                    elif type(node) == OperandNode:
                        node.append(item.visit())
                    else: temp.append(node.expression.visit())
                else:
                    temp.append(node)
            
            # remove leaf nodes
            nodes = [ item for item in temp if type(item) not in leaf_nodes]

            if all(isinstance(x, BinaryExpressionNode) for x in nodes):
                break

        # check operand data type for all binary expressions  
        for node in nodes:
            operands = node.getInner()

            error = False
            # if at least one operand is of type STR, then error
            for operand in operands:
                if type(operand) == int:
                    continue
                elif type(operand) == str and self.symbol_table[operand]['type'] == 'STR':
                    error = True
                    break

            # replace current node to error node
            if error:
                err = f'Incompatible data types for operation for \'{node.operation.value}\' at line {node.line_num}'
                self.errors.append(err)

    # assign values for variables without initial values
    # this modifies the symbol table 
    def assignVariables(self):
        node = self.ast.visit()
        node = [ item for item in node if type(item) == VariableDeclarationNode]

        # assign initial values
        for item in node:
            if item.expression == None:
                if item.data_type == TOKEN.INT: # assign 0 to int vars
                    self.symbol_table[item.var_name]['value'] = 0
                else:                           # assign empty string
                    self.symbol_table[item.var_name]['value'] = ''

    # checks for undeclared identifiers in the symbol table
    # appends semantic errors found while processing
    def checkUndeclaredVariables(self):
        for key in self.symbol_table:
            if self.symbol_table[key]['type'] == None:
                line = self.symbol_table[key]['line_num']
                err = f'Reference to an undeclared variable \'{key}\' at line {line}'
                self.errors.append(err)

    # returns a formatted list of the semantic errors
    def getSemanticErrors(self):
        errorsFormatted = []
        for error in self.errors:
            errorsFormatted.append(f'Semantic Error: {error}')
        return errorsFormatted


