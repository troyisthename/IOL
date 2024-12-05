from IOL_lexer import *
from IOL_ast import *
from IOL_parser import *
from IOL_semantic_analyzer import *
from IOL_executor import *

# main flow of the compiler upto semantic analyzer
class Main:
    def compiler(src):
        with open(src, 'r') as f:
            inputs = f.read()

        # tokenize the code
        lexer = Lexer(inputs)
        
        # generate the .tkn file, variable list, and invalid lexemes list
        lexer.generate_tknFile(src.replace('.iol', '.tkn'))
        varList = lexer.get_varList()
        invalidLexemes = lexer.get_invalidLexemes()
        
        # format the variable list and invalid lexemes list for display
        varListFormatted = []   
        for key in varList:
            varListFormatted.append('{}, {}'.format(key, varList[key]['type']))

        # get all lexical errors
        errorsFormatted = []
        for ilexeme in invalidLexemes:
            errorsFormatted.append('Lexical Error: unknown word \'{}\' found in line {}'.format(ilexeme[0], ilexeme[1]))

        # parser start
        symbol_table = lexer.get_varList()      # symbol table
        parser = Parser(lexer)                  # parser

        # if the root node of the AST is not a ProgramNode, don't proceed to semantic analysis
        if type(parser.program_node) != ProgramNode:
            syntax_errors = parser.program_node.visit()
            msg = f'{syntax_errors.value} at line {syntax_errors.line_num}'
            errorsFormatted.append(msg)
            

        else:   # proceed if root node is a ProgramNode
            syntax_errors = parser.getSyntaxErrors()
            symbol_table = parser.verifyVariableType(symbol_table)
            semantic_analyzer = SemanticAnalyzer(parser.program_node, symbol_table)
            
            # get updated symbol table
            symbol_table = semantic_analyzer.symbol_table
            semantic_errors = semantic_analyzer.getSemanticErrors()

            # append syntax and semantic errors found in processing for display
            for item in syntax_errors:
                errorsFormatted.append(item)
            
            for item in semantic_errors:
                errorsFormatted.append(item)

        # return a list
        return varListFormatted, errorsFormatted, parser.program_node, symbol_table