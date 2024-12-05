from IOL_lexer import *
from IOL_ast import *

'''
 allows for the creation of the AST representation of a given stream of tokens through top down parsing
 makes use of the classes defined in IOL_ast.py file
 also, the class used for syntax analysis of the provided token stream 
 and responsible for adding line number in declared variables and verifying its data types in the symbol table
'''
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = lexer.tokens
        
        self.curr_tok = self.lexer.getToken()   # pointer for current token being processed
        self.next_tok = self.lexer.getToken()   # pointer for next token to be processed

        self.errors = []

        # parse code
        self.program_node = self.parseCode()
        
        
    # moves the next token to the current token 
    # and acquires the next token from the lexer object
    def consumeToken(self):
        self.curr_tok = self.next_tok
        self.next_tok = self.lexer.getToken()

    # checks if the source code follows the grammar of the program based on generated tokens
    # program → 'IOL' {statement} 'LOI'
    # returns an instance of ProgramNode if the source code follows the grammar
    # else it returns an ErrorNode
    def parseCode(self):
        # check if there is only one IOL and LOI tokens
        IOL_count = 0
        LOI_count = 0

        for token in self.tokens:
            if token.token_type == TOKEN.IOL:
                IOL_count += 1
            elif token.token_type == TOKEN.LOI:
                LOI_count += 1
            else: continue

        if self.tokens[0].token_type != TOKEN.IOL:    # no IOL token at the beginning
            return ErrorNode('Missing \'IOL\' keyword', 1)
        
        
        # consume IOL token
        self.consumeToken()
        
        # parse program node
        program_node = ProgramNode(self.parseProgramNode())
        
        # check for the prescence of token LOI
        
        # EOF is not the last token and current token is LOI
        if self.next_tok.token_type != TOKEN.EOF and self.curr_tok.token_type == TOKEN.LOI:        
            return ErrorNode(f'Unexpected keyword \'{self.next_tok.value}\' after LOI', self.curr_tok.line_num)
 
        elif self.curr_tok.token_type != TOKEN.LOI:       # LOI is not the 2nd to last token, excluding EOF
            return ErrorNode('Missing \'LOI\' keyword', self.tokens[-1].line_num)

        # successfully parsed
        return program_node

    # returns a list of StatementNodes (i.e the statements of the program)
    # generates an ErrorNode if ERR_LEX is encoutnered
    def parseProgramNode(self):
        statement_nodes = []

        # parse current token until 'LOI' or 'EOF' is encountered
        while self.curr_tok.token_type != TOKEN.LOI and self.curr_tok.token_type != TOKEN.EOF:
            # check if current token is an TOKEN.ERR_LEX
            if self.curr_tok.token_type == TOKEN.ERR_LEX:
                statement_nodes.append(ErrorNode(f'Invalid keyword \'{self.curr_tok.value}\'', self.curr_tok.line_num))
                self.consumeToken()
                continue

            # else, parse statement
            else:
                statement_nodes.append(self.parseStatementNode())

        return statement_nodes

    # calls the specific function for parsing a statement node 
    # based on the first word encountered in the statement
    # returns a specific statement node for the parsed statement
    def parseStatementNode(self):
        statement = None

        # variable declaration if it starts with 'INT' or 'STR'
        if self.curr_tok.token_type == TOKEN.INT or self.curr_tok.token_type == TOKEN.STR:
            return self.parseVariableDeclaration()

        # variable assignment if it starts with 'INTO'
        elif self.curr_tok.token_type == TOKEN.INTO:
            return self.parseAssignmentNode()

        # input operation if it starts with 'BEG'
        elif self.curr_tok.token_type == TOKEN.BEG:
            return self.parseInputOperation()

        # newline operation if it starts with 'NEWLN'
        elif self.curr_tok.token_type == TOKEN.NEWLN:
            return self.parseNewlineOperation()

        # output operation if it starts with 'PRINT'
        elif self.curr_tok.token_type == TOKEN.PRINT:
            return self.parseOutputOperation()

        # if 'LOI' was encountered
        elif self.curr_tok.token_type == TOKEN.LOI:
            line_num = self.curr_tok.line_num
            value = self.curr_tok.value
            self.consumeToken()
            return ErrorNode(f'Unexpected keyword \'LOI\'', line_num)

        # if EOF (end of file) is encountered
        elif self.curr_tok.token_type == TOKEN.EOF:
            line_num = self.curr_tok.line_num
            value = self.curr_tok.value
            self.consumeToken()
            return ErrorNode(f'Unexpected end of program', line_num)

        else:   # an unexpected token
            line_num = self.curr_tok.line_num
            value = self.curr_tok.value
            self.consumeToken()
            return ErrorNode(f'Unexpected token \'{value}\'', line_num)

    # returns an instance of NewlineNode
    def parseNewlineOperation(self):
        line_num = self.curr_tok.line_num
        # consume token NEWLN
        self.consumeToken()

        return NewlineNode(self.curr_tok.line_num)
    
    # returns an instance of OutputNode
    # also calls the appropriate function for parsing the expression associated with the output statement
    def parseOutputOperation(self):
        line_num = self.curr_tok.line_num
        # consume token PRINT
        self.consumeToken()

        expression = self.parseExpression()

        return OutputNode(expression, line_num)

    # parses the input operation statement based on the grammar
    # returns an instance of InputNode, if parsing is successful; else, an ErrorNode
    def parseInputOperation(self):

        line_num = self.curr_tok.line_num
        # consume token BEG
        self.consumeToken()

        # invalid if next token is not an IDENT
        if self.curr_tok.token_type != TOKEN.IDENT:
            line_num = self.curr_tok.line_num
            value = self.curr_tok.value
            self.consumeToken()
            return ErrorNode(f'Expected identifier after keyword \'BEG\', instead got token \'{value}\'', line_num)

        var_name = self.curr_tok.value
        # consume IDENT token
        self.consumeToken()

        return InputNode(var_name, line_num)

    # parses the assignment operation statement based on the grammar
    # returns an instance of AssignmentNode, if parsing is successful; else, an ErrorNode
    def parseAssignmentNode(self):

        line_num = self.curr_tok.line_num
        # consume INTO token
        self.consumeToken()

        # invalid if current token is not an IDENT
        if self.curr_tok.token_type != TOKEN.IDENT:
            line_num = self.curr_tok.line_num
            value = self.curr_tok.value
            self.consumeToken()
            return ErrorNode(f'Unexpected token \'{value}\' after keyword \'INTO\'', line_num)

        identifier = self.curr_tok.value
        # consume IDENT token
        self.consumeToken()

        # invalid if current token is not IS
        if self.curr_tok.token_type != TOKEN.IS:
            line_num = self.curr_tok.line_num
            value = self.curr_tok.value
            self.consumeToken()
            return ErrorNode(f'Unexpected keyword \'{value}\' after an identifier in an assignement', line_num)

        # consume IS token
        self.consumeToken()

        # parse expression
        expression = self.parseExpression()

        return AssignmentNode(identifier, expression, line_num)

    # parses the variable declaration statement based on the grammar
    # returns an instance of VariableDeclarationNode, if parsing is successful; else, an ErrorNode
    # also calls the appropriate function for parsing the optional expression associated with it 
    def parseVariableDeclaration(self):
        # get data type
        var_type = self.curr_tok.token_type
        self.consumeToken()

        # invalid if current token is not an IDENT
        if self.curr_tok.token_type != TOKEN.IDENT:
            # get token details
            value = self.curr_tok.value
            line_num = self.curr_tok.line_num
            self.consumeToken()
            return ErrorNode(f'Unexpected token \'{value}\' after a data type', line_num)

        # save ident name and line number for saving later
        var_name = self.curr_tok.value
        line_num = self.curr_tok.line_num
        # consume IDENT token
        self.consumeToken()

        # return the declaration node if declaration is data_type var_name
        if self.curr_tok.token_type != TOKEN.IS:
            return VariableDeclarationNode(var_type, var_name, line_num)

        # consume token 'IS' 
        self.consumeToken()

        # parse expression
        expression = self.parseExpression()

        return VariableDeclarationNode(var_type, var_name, line_num, expression)

    # calls a specific function for parsing an expression node 
    # based on the first word encountered in the expression
    # returns a specific expression node for the parsed expression
    def parseExpression(self):
        operation = self.curr_tok.token_type
        line_num = self.curr_tok.line_num

        # expression is a arithmetic/binary operation
        if (operation == TOKEN.ADD 
            or operation == TOKEN.SUB
            or operation == TOKEN.MULT
            or operation == TOKEN.DIV
            or operation == TOKEN.MOD):
            self.consumeToken();
            left = self.parseExpression()
            right = self.parseExpression()

            if type(left) != ErrorNode and type(right) != ErrorNode:
                return BinaryExpressionNode(operation, left, right, line_num)
            
            # return an error node if either left or right expressions returned an ErrorNode
            if type(left) == ErrorNode:
                return left
            else:
                return right 

        # expression is just an identifier
        elif (operation == TOKEN.IDENT
            or operation == TOKEN.INT_LIT):
            return OperandNode(self.parseOperand(), line_num)

        # expression is the end of file
        elif (operation == TOKEN.EOF):
            return ErrorNode(f'Unexpected end of program', line_num)

        else:   # unexpected token encountered for expression
            value = self.curr_tok.value
            self.consumeToken();
            return ErrorNode(f'Unexpected token \'{value}\'', line_num)

    # calls a specific function for parsing an operand node 
    # based on the current token token type
    # returns a specific expression node for the parsed operand 
    def parseOperand(self):
        op_type = self.curr_tok.token_type
        value = self.curr_tok.value
        line_num = self.curr_tok.line_num
        
        # consume operand
        self.consumeToken()

        # operand is an integer literal
        if op_type == TOKEN.INT_LIT:
            return NumericLiteralNode(int(value), line_num)
        
        # operand is an identifier
        elif op_type == TOKEN.IDENT:
            return IdentifierNode(value, line_num)

        # operand is a the end of file
        elif (op_type == TOKEN.EOF):
            return ErrorNode(f'Unexpected end of program', line_num)

        else:   # unexpected token encountered for operand
            return ErrorNode(f'Unexpected token \'{value}\'', line_num)

    # verifies the data type of each identifier based on the VariableDeclarationNode
    # also adds line number information on the table
    def verifyVariableType(self, symbol_table):
        # visit all VariableDeclarationNodes
        node = [ item for item in self.program_node.visit() if type(item) == VariableDeclarationNode]

        # compare current data type in symbol table and the data type used in var declaration
        for item in node:
            temp = {symbol_table[item.var_name]['type']}
            
            
            # edit data_type if they do not match, 
            if item.data_type.value != symbol_table[item.var_name]['type']:
                # ignore double declarations
                if 'line_num' not in symbol_table[item.var_name]:
                    symbol_table[item.var_name]['type'] = item.data_type.value 

            # add line number in symbol table
            symbol_table[item.var_name]['line_num'] = item.line_num

        return symbol_table


    # function that returns the list of all syntax errors by visiting all ErrorNodes generated     
    def getSyntaxErrors(self):
        node = self.program_node.visit()
        # ignore these nodes
        leaf_nodes = [NewlineNode, IdentifierNode, NumericLiteralNode, InputNode]

        # remove leaf nodes in node list
        node = [item for item in node if type(item) not in leaf_nodes]
        
        
        # collate all error nodes by visiting all nodes
        while True:
            temp = []
            for item in node:
                if type(item) != ErrorNode:
                    # remove if expression is None in the declaration node
                    if type(item) == VariableDeclarationNode and item.expression == None:
                        continue 
                    elif type(item) == BinaryExpressionNode:
                        temp.append(item.left.visit())
                        temp.append(item.right.visit())
                    elif type(item) == ExpressionNode:
                        temp.append(item.visit())
                    elif type(item) == OperandNode:
                        temp.append(item.visit())
                    else: temp.append(item.expression.visit())
                else:
                    temp.append(item)
            
            # remove leaf nodes
            node = [ item for item in temp if type(item) not in leaf_nodes]

            if all(isinstance(x, ErrorNode) for x in node):
                break

        # collect and format all syntax errors
        for item in node:
            msg = f'Syntax Error: {item.value} at line {item.line_num}'
            self.errors.append(msg)

        return self.errors
