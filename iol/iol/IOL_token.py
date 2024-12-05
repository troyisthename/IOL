from enum import Enum, unique

# token names
@unique
class TOKEN(Enum):
    # int literal
    INT_LIT = 'INT_LIT'

    # keywords
    IOL = 'IOL'
    LOI = 'LOI'
    INTO = 'INTO'
    IS = 'IS'
    BEG = 'BEG'
    PRINT = 'PRINT'
    NEWLN = 'NEWLN'
    INT = 'INT'
    STR = 'STR'

    # arithmetic operations
    ADD = 'ADD'
    SUB = 'SUB'
    MULT = 'MULT'
    DIV = 'DIV'
    MOD = 'MOD'


    # others
    IDENT = 'IDENT'
    EOF = 'EOF'
    ERR_LEX = 'ERR_LEX'

# blueprint class for IOL tokens -- also stores the line number of token
class Token:
     def __init__(self, token_type, value, line_num):
        self.token_type = self.determineTokenType(token_type, value)
        self.value = value
        self.line_num = line_num

     # determines the token-type basesd on values passed
     def determineTokenType(self, token_type, value):
        # int literal
        if token_type == TOKEN.INT_LIT:
            return TOKEN.INT_LIT
       
        # keywords
        elif token_type == TOKEN.IDENT:
            # keywords
            if value == TOKEN.IOL.value:
                return TOKEN.IOL
            elif value == TOKEN.LOI.value:
                return TOKEN.LOI
            elif value == TOKEN.INTO.value:
                return TOKEN.INTO
            elif value == TOKEN.IS.value:
                return TOKEN.IS
            elif value == TOKEN.BEG.value:
                return TOKEN.BEG
            elif value == TOKEN.PRINT.value:
                return TOKEN.PRINT
            elif value == TOKEN.NEWLN.value:
                return TOKEN.NEWLN
            # data types
            elif value == TOKEN.INT.value:
                return TOKEN.INT
            elif value == TOKEN.STR.value:
                return TOKEN.STR
            # arithmetic/binary operators
            elif value == TOKEN.ADD.value:
                return TOKEN.ADD
            elif value == TOKEN.SUB.value:
                return TOKEN.SUB
            elif value == TOKEN.MULT.value:
                return TOKEN.MULT
            elif value == TOKEN.DIV.value:
                return TOKEN.DIV
            elif value == TOKEN.MOD.value:
                return TOKEN.MOD
            # identifier
            else:
                return TOKEN.IDENT

        # token to indicate end of file
        elif token_type == TOKEN.EOF:
            return TOKEN.EOF

        # token for invalid lexemes
        else:
            return TOKEN.ERR_LEX