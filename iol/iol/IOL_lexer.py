from IOL_token import *	#import TOKEN and Token class
import re

'''
 allows for the tokenization of a given source file
 makes use of the token class to create tokens
'''
class Lexer:
	# regex for identifiers/var name and int literals
	var_name_pattern = re.compile('[a-zA-Z][^\W_]*')
	int_literal_pattern = re.compile('[0-9]+') 
	
	def __init__(self, srcCode):
		self.srcCode = srcCode.rstrip()
		self.tokens = []
		self.current_token = 0	# position of current token being accessed
		self.current_index = 0	# position of current character being processed

		self.token_count = 0	# number of tokens stored

		# tokenize source code until the last character
		while self.current_index <= len(self.srcCode):
			tok = self.nextToken()
			# print('TOKEN: {} {} {}'.format(tok.token_type, tok.value, tok.line_num))
			self.tokens.append(tok)
			self.token_count += 1
			# print('tok count: {}'.format(self.token_count))

	# used to return a token from the tokens list, utilized in parsing stage
	def getToken(self): 
		if self.current_token < len(self.tokens):
			token = self.tokens[self.current_token]
			self.current_token += 1
			return token
		else:
			return Token(TOKEN.ERR_LEX, 'Final token surpassed' , -1)

	# decode the next token's type and value
	# temporarily sets the token_type of any keyword to IDENT
	def nextToken(self):
		while self.current_index < len(self.srcCode) and self.srcCode[self.current_index] != None:
			if self.srcCode[self.current_index].isspace():
				self.skip()

			else:
				lexeme = self.get_lexeme()
				# test if valid int literal
				result = self.int_literal_pattern.match(lexeme)
				if result != None and result.group(0) == lexeme:
					return Token(TOKEN.INT_LIT, lexeme, self.get_lineNumber())

				# test if valid keyword or identifier
				result = self.var_name_pattern.match(lexeme)
				if result != None and result.group(0) == lexeme:
					return Token(TOKEN.IDENT, lexeme, self.get_lineNumber())

				else:
					return Token(TOKEN.ERR_LEX, lexeme, self.get_lineNumber())

		self.current_index += 1
		# return end of file token
		return Token(TOKEN.EOF, '\0', len(self.srcCode.rstrip().split('\n')))
	
	# increment current_index value while not EOF 
	def nextChar(self):
		if self.srcCode[self.current_index] != None and self.current_index < len(self.srcCode):
			self.current_index += 1

	# skip whitespaces
	def skip(self):
		while self.srcCode[self.current_index].isspace() and self.srcCode[self.current_index] != None:
			self.nextChar()

	# returns the whole word from current_index 
	def get_lexeme(self):
		lexeme = ""
		while (	self.current_index < len(self.srcCode) 
			   	and self.srcCode[self.current_index] != None 
			   	and not self.srcCode[self.current_index].isspace()):
			lexeme += self.srcCode[self.current_index]
			self.current_index += 1

		return lexeme

	# returns the line number of the current char
	def get_lineNumber(self):
		line_num = 1
		for i in range(self.current_index):
			if self.srcCode[i] == '\n':
				line_num += 1
		return line_num

	# generates the .tkn file which contains the stream of tokens while preserving the whitespaces
	def generate_tknFile(self, outputDir):
		outputDir = outputDir
		tokenizedSrc = self.srcCode
		startIndex = 0

		for token in self.tokens:
			# current token is EOF
			if token.token_type == TOKEN.EOF:
				 tokenizedSrc +=  '<{},{}>'.format(token.token_type.value, token.value.encode('utf-8'))
				 continue

			# replace the lexeme to its appropriate token
			add = '<{},{}>'.format((token.token_type).value, token.value)
			tokenizedSrc = tokenizedSrc[:startIndex] + tokenizedSrc[startIndex:].replace(token.value, add, 1)
			
			# find index of the replaced string
			result = tokenizedSrc[startIndex:].index(add)
		
			# move the startIndex to the last char of the previously replaced string
			startIndex = startIndex + result + len(add)

		with open(outputDir, 'w') as f:
			f.write(tokenizedSrc)
				
	# returns a dictionary of variables
	def get_varList(self):
		varList = {}
		for i in range(len(self.tokens)):
			if self.tokens[i].token_type == TOKEN.IDENT and self.tokens[i].value not in varList:
				if self.tokens[i-1].token_type != TOKEN.INT and self.tokens[i-1].token_type != TOKEN.STR:
					# set the type to none for variables that are not declared properly 
					varList[self.tokens[i].value] = {'type': None, 'line_num': self.tokens[i].line_num}
					continue
				varList[self.tokens[i].value] = {'type': self.tokens[i-1].value}

		return varList

	# returns a list of invalid lexemes and their line number
	def get_invalidLexemes(self):
		invalidLexemes = []
		for item in self.tokens:
			if item.token_type == TOKEN.ERR_LEX:
				invalidLexemes.append((item.value, item.line_num))

		return invalidLexemes
			