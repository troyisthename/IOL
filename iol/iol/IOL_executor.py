from IOL_semantic_analyzer import *
from ui import *
from tkinter import simpledialog

# allows for the execution of a given AST and symbol table
# interacts with an instance of the class App to manipulate the ui window
class Executor:
    def __init__(self, app, ast, symbol_table):
        self.app = app

        self.ast = ast

        self.symbol_table = symbol_table

        self.currentExprType = None     # current data type of the current operation 
        self.currentExprValue = None    # current value of the current operation 
        self.currentIdentifier = None   # current identifier of the current operation 

        # for console display 
        self.consoleInsert('IOL Execution:\n')
        self.executeProgram()

    # inserts a given content to the ui's console window
    def consoleInsert(self, out):
        self.app.contentEditable(True)
        self.app.consoleContent.insert(END, out)
        self.app.contentEditable(False)

    # prints a new line in the console window
    def executeNewlineNode(self, node):
        self.consoleInsert('\n')

    # updates current expression type, value, and identifier based on the given node
    # if identifier is undeclared or used before declaration, returns an ErrorNode
    def executeIdentifier(self, node):
        # check if undeclared variable
        if 'value' not in self.symbol_table[node.var_name]:
            return ErrorNode(f'\'{node.var_name}\' is not defined', node.line_num)
        
        # identifier used before declaration
        elif 'value' in self.symbol_table[node.var_name] and node.line_num < self.symbol_table[node.var_name]['line_num']:
            return ErrorNode(f'\'{node.var_name}\' used before declaration', node.line_num)

        # identifier declared before used
        elif 'value' in self.symbol_table[node.var_name]:
            self.currentExprType = self.symbol_table[node.var_name]['type']
            self.currentExprValue = self.symbol_table[node.var_name]['value']
            self.currentIdentifier = node.var_name
    
    # updates the current expression type and value based on the given node
    def executeNumericLiteralNode(self, node):
        self.currentExprType = 'INT'
        self.currentExprValue = node.value

    # updates the current expression type, value, and identifier based on the result of the arithemtic/binary operation
    # returns an ErrorNode for division or modulo by zero
    def executeBinaryExpressionNode(self, node):
        operation = node.operation

        # visit left node, obtain its type and value
        if type(self.execute(node.left.visit())) == ErrorNode:
            return self.execute(node.left.visit())
        left_type = self.currentExprType 
        left_value = self.currentExprValue 

        # visit right node, obtain its type and value
        if type(self.execute(node.right.visit())) == ErrorNode:
            return self.execute(node.right.visit())
        right_type = self.currentExprType 
        right_value = self.currentExprValue

        result = None

        # if both operands are INT, execute operation to update current expression and value
        if left_type == 'INT' and right_type == 'INT':
            # update current expression
            self.currentExprType = 'INT'    

            # execute operation
            if operation == TOKEN.ADD:
                result = int(left_value + right_value)
            elif operation == TOKEN.SUB:
                result = int(left_value - right_value)
            elif operation == TOKEN.MULT:
                result = int(left_value * right_value)
            elif operation == TOKEN.DIV:
                if right_value == 0:    # division by 0 is not allowed
                    return ErrorNode(f'Division by zero[0]', node.line_num)
                result = int(left_value / right_value)
            elif operation == TOKEN.MOD:
                if right_value == 0:    # modulo by 0 is not allowed
                    return ErrorNode(f'Modulo by zero[0]', node.line_num)
                result = int(left_value % right_value)

            # update current expression value
            self.currentExprValue = result
        else:   # at least one operand is of type 'STR'
            return ErrorNode(f'Incompatible types found for operation {operation}. Expected two numerical expressions but at least one given is not', node.line_num)

    # prints athe result of the node expression at the console window
    # returns an ErrorNode if expression returns an ErrorNode
    def executeOutputNode(self, node):
        self.currentIdentifier = '\0'
        # visit expression to update current value and type
        if type(self.execute(node.expression.visit())) == ErrorNode:
            return self.execute(node.expression.visit())

        # add to ouput list
        out = f'{self.currentExprValue}'
        self.consoleInsert(out)

    # asks an input from the user via pop-up window
    # returns an ErrorNode if no input received from the user; else it updates the symbol table
    def executeInputNode(self, node):
        # update current expr type, value and identifier
        self.currentExprType = self.symbol_table[node.var_name]['type']
        self.currentExprValue = self.symbol_table[node.var_name]['value']
        self.currentIdentifier = node.var_name

        # show input dialog
        input_value = simpledialog.askstring('BEG operation', f'Input for {self.currentIdentifier}:')

        # no input received
        if input_value is None:
            return ErrorNode(f'No input received for BEG operation of {self.currentIdentifier}', node.line_num)

        # input will be assigned to an identifier of type INT
        if self.currentExprType == 'INT':
            import re
            int_literal_pattern = re.compile('[0-9]+')  # regex of IOL int

            # test if input is valid int literal
            result = int_literal_pattern.match(input_value)
            if result == None or result.group(0) != input_value:
                return ErrorNode(f'Incompatible input for declared data type of {node.var_name}', node.line_num)

            input_value = int(input_value) # convert input to int

        # update symbol table value of ident   
        self.symbol_table[node.var_name]['value'] = input_value
        self.currentExprValue = input_value

    # updates the symbol table based on the var name and resulting value of the expression of the node
    # returns an ErrorNode if expression returns an ErrorNode or incompatible data types
    def executeAssignmentNode(self, node):
        if type(self.execute(node.expression.visit())) == ErrorNode:
            return self.execute(node.expression.visit())
        
        # check if both identifier and current expression are of the same data type
        if self.symbol_table[node.var_name]['type'] != self.currentExprType:
            s_type = self.symbol_table[node.var_name]['type']
            return ErrorNode(f'Incompatible types found for assignment operation. Expected {s_type} expression but given is {self.currentExprType}', node.line_num)

        # update symbol table value of identifier   
        self.symbol_table[node.var_name]['value'] = self.currentExprValue 

    # updates the symbol table based on the var name and resulting value of the expression of the node
    # returns an ErrorNode for incompatible data types
    def executeVariableDeclarationNode(self, node):
        if node.expression != None and type(self.execute(node.expression.visit())) == ErrorNode:
            return self.execute(node.expression.visit())

        elif node.expression == None:
            if node.data_type == TOKEN.INT:
                self.currentExprValue = 0
                self.currentExprType = 'INT'
            else:
                self.currentExprValue = ''
                self.currentExprType = 'STR'

        # check if both identifier and current expression are of the same data type
        if self.symbol_table[node.var_name]['type'] != self.currentExprType:
            s_type = self.symbol_table[node.var_name]['type']
            return ErrorNode(f'Incompatible types found for assignment operation. Expected {s_type} expression but given is {self.currentExprType}', node.line_num)

        # update symbol table value of identifier   
        self.symbol_table[node.var_name]['value'] = self.currentExprValue

    # helper function that calls the appropriate function based on the type of the node passed
    def execute(self, node):
        node_type = type(node)

        if node_type == VariableDeclarationNode:
            return self.executeVariableDeclarationNode(node)

        elif node_type == AssignmentNode:
            return self.executeAssignmentNode(node)
        
        elif node_type == InputNode:
            return self.executeInputNode(node)

        elif node_type == OutputNode:
            return self.executeOutputNode(node)

        elif node_type == BinaryExpressionNode:
            return self.executeBinaryExpressionNode(node)

        elif node_type == NumericLiteralNode:
            return self.executeNumericLiteralNode(node)

        elif node_type == IdentifierNode:
            return self.executeIdentifier(node)

        elif node_type == NewlineNode:
            return self.executeNewlineNode(node)

    # visits and executes all codes by calling appropriate function for each node
    # if a node returns ErrorNode, execution is halted and error message is printed at the console window
    # if successful execution, prints success message at the console window
    def executeProgram(self):
        nodes = self.ast.visit()

        # visit and execute all nodes
        for node in nodes:
            temp = self.execute(node)
            # if execution returns an ErrorNode, immediately halt execution and print the error
            if type(temp) == ErrorNode:
                # print error message
                err = f'\n\nExecution Error: {temp.value} at line {temp.line_num}.\nTerminating program...'
                self.consoleInsert(err)
                return

        # print success message
        out = '\n\nProgram terminated successfully...'
        self.consoleInsert(out)
        return
