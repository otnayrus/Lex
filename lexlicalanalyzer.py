import re
from enum import Enum
from tabulate import tabulate

class TokenType(Enum):
	TAG_OPEN_SYMBOL = 0
	TAG_CLOSE_SYMBOL = 1
	TAG_ASSIGNMENT_SYMBOL = 2
	TAG_NAME = 3
	TAG_ATTRIBUTE_NAME = 4
	TAG_ATTRIBUTE_VALUE = 5
	TAG_IDENTIFIER = 6
	RAW_DATA = 7
	COMMENT_OPEN = 8
	COMMENT_CLOSE = 9
	ALPHABET = 10
	ELEMENT = 11
	DOCUMENT_TYPE = 12
	UNKNOWN_DATA = 13
	CSS_SECTION = 14
	JS_SECTION = 15
	CSS_SECTION1 = 16
	JS_SECTION1 = 17

class Token:
	def __init__(self,idx,string,tokentype):
		self.idx = idx
		self.html = string
		self.type = tokentype;

def Generate(string,idx):
	re_document_type = re.compile("<!.* html>")
	re_comment_open = re.compile("\<!--")
	re_open_tag = re.compile("""(<([a-z0-9]+)([a-zA-Z0-9 '",.-_#]*?)>)""")
	re_self_closing_tag = re.compile("""(<([a-z0-9]+)([a-zA-Z0-9 ='",.\-_:/]*?)\/>)""")
	re_raw_data = re.compile(">.+<")
	re_close_tag = re.compile("""(</([a-z0-9]+)(?!\/)>)""")
	re_comment_close = re.compile("(.)*(-->)")
	re_raw_data2 = re.compile(".+")
	
	global list_token
	global tokens
	tokens = []

	result_document_type 	= re_document_type.findall(string)
	result_comment_open 	= re_comment_open.findall(string)
	result_comment_close 	= re_comment_close.findall(string)
	result_open_tag 		= re_open_tag.findall(string)
	result_close_tag 		= re_close_tag.findall(string)
	result_self_closing_tag = re_self_closing_tag.findall(string)
	result_raw_data 		= re_raw_data.findall(string)

	if(result_comment_open == [] and
		result_comment_close == [] and
		result_open_tag == [] and
		result_close_tag == [] and
		result_self_closing_tag == [] and
		result_raw_data == [] and
		result_document_type == []) :
		result_raw_data2		= re_raw_data2.findall(string)
	else :
		result_raw_data2		= []
		
	tokenize(idx,result_document_type,'document_type')
	tokenize(idx,result_comment_open,'comment_open')
	tokenize(idx,result_open_tag,'open_tag')
	tokenize(idx,result_self_closing_tag,'self_closing_tag')
	tokenize(idx,result_raw_data,'raw_data')
	tokenize(idx,result_raw_data2,'raw_data2')
	tokenize(idx,result_close_tag,'close_tag')
	tokenize(idx,result_comment_close,'comment_close')
	#print(result_raw_data2,idx)
	list_token.append(tokens)
	
def tokenize(idx,results,tipe):
	global tokens
	if tipe == 'comment_open' and results:
		tokens.append(Token(idx,'== COMMENT OPEN ==',TokenType.ELEMENT))
	if tipe == 'open_tag' and results: 
		tokens.append(Token(idx,'== OPENING TAG ==',TokenType.ELEMENT))
	if tipe == 'self_closing_tag' and results:
		tokens.append(Token(idx,'== SELF CLOSING TAG ==',TokenType.ELEMENT))
	if tipe == 'close_tag' and results:
		tokens.append(Token(idx,'== CLOSING TAG ==',TokenType.ELEMENT))
	if tipe == 'comment_close' and results:
		tokens.append(Token(idx,'== COMMENT CLOSE ==',TokenType.ELEMENT))
	if tipe == 'document_type' and results:
		tokens.append(Token(idx,'== DOCUMENT TYPE ==',TokenType.ELEMENT))
	for result in results:
		if result == None : return
		if tipe == 'raw_data' :
			tokens.append(Token(idx,''.join(map(str,result))[1:-1],TokenType.RAW_DATA))
			continue
		if tipe == 'raw_data2' :
			tokens.append(Token(idx,''.join(map(str,result)),TokenType.UNKNOWN_DATA))
			continue
		if tipe == 'comment_open':
			tokens.append(Token(idx,''.join(map(str,result)),TokenType.COMMENT_OPEN))
		if tipe == 'open_tag' or tipe == 'self_closing_tag':
			res = ''.join(map(str,result))
			if(res == '/') and tipe != 'self_closing_tag':
				continue
			tokens.append(Token(idx,result[0],TokenType.TAG_OPEN_SYMBOL))
			tagName = result[0]
			tokens.append(Token(idx,tagName,TokenType.TAG_NAME))
			attribute = parse_attr(result[0])
			for attr in attribute:
				if '=' in attr:
					attr = attr.split('=')
					tokens.append(Token(idx,attr[0],TokenType.TAG_ATTRIBUTE_NAME))
					tokens.append(Token(idx,'=',TokenType.TAG_ASSIGNMENT_SYMBOL))
					tokens.append(Token(idx,attr[1],TokenType.TAG_ATTRIBUTE_VALUE))
				else :
					attr = attr.strip()
					if attr != "" : 
						tokens.append(Token(idx,attr,TokenType.TAG_IDENTIFIER))
		if tipe == 'close_tag' :
			tokens.append(Token(idx,result[0],TokenType.TAG_NAME))
		if tipe == 'comment_close':
			tokens.append(Token(idx,result[0],TokenType.COMMENT_OPEN))
		if tipe == 'document_type':
			tokens.append(Token(idx,''.join(map(str,result)),TokenType.DOCUMENT_TYPE))
		
def parse_attr(string):
	list_attr = []
	count_quote = 0
	idx = 0
	while True :
		try :
			if string[idx] == ' ' and count_quote!=1:
				list_attr.append(string[idx])
				string = string[idx+1:]
				idx = 0
			if string[idx] == '"' or string[idx] == "'" : 
				count_quote+=1
			if count_quote == 2:
				list_attr.append(string[:idx+1])
				string = string[idx+1:]
				idx = 0
				count_quote = 0
		except IndexError :
			break
		idx+=1
	return list_attr
	
def initiate(filename):
	global files
	re_css = re.compile("(.*)?(?=<style>)(<style>)([^\n]*)")
	re_js = re.compile("(.*)?(?=<script>)(<script>)([^\n]*)")
	re_close_css = re.compile("</style>")
	re_close_js = re.compile("</script>")
	re_any = re.compile(".+")
	i = 0
	css = 0
	js = 0
	with open(filename,'r+') as f :
		for line in f :
			result_css = re_css.findall(line)
			result_js = re_js.findall(line)
			result_close_css = re_close_css.findall(line)
			result_close_js = re_close_js.findall(line)
			result_any = re_any.findall(line)
			if result_css and css == 0 and js == 0:
				css += 1
			elif result_js and css == 0 and js == 0:
				js += 1
			if result_close_css and css > 0:
				css -= 1
			elif result_close_js and js > 0:
				js -= 1
				
			if css == 0 and js == 0:
				Generate(line,i)
				
			else:
				global list_token
				tokens = []
				if css > 0 :
					if result_css:
						if result_css[0][0] != '\n' and result_css[0][0]!='' : Generate(result_css[0][0],i)
						Generate(result_css[0][1],i)
						if result_css[0][2] != '\n' and result_css[0][2]!='' : tokens.append(Token(i,''.join(map(str,result_css[0][2])),TokenType.CSS_SECTION1))
					else:
						tokens.append(Token(i,''.join(map(str,result_any)),TokenType.CSS_SECTION))
				elif js > 0 :
					if result_js:
						if result_js[0][0] != '\n' and result_js[0][0]!='' : Generate(result_js[0][0],i)
						Generate(result_js[0][1],i)
						if result_js[0][2] != '\n' and result_js[0][2]!='' : tokens.append(Token(i,''.join(map(str,result_js[0][2])),TokenType.JS_SECTION1))
					else:
						tokens.append(Token(i,''.join(map(str,result_any)),TokenType.JS_SECTION))
				list_token.append(tokens)
			i+=1	
			
		
def printout():
	global list_token
	row_i = 0
	
	for tokens in list_token:
		x = [['Token','Type']]
		for tok in tokens:
			if(tok.type == TokenType.ELEMENT) :
				x.append([tok.html,' '])
			else :
				x.append([tok.html,tok.type.name])
		print(tabulate(x))
		print()
#-----------------------------------------
list_token = [];
initiate('test.html')
printout()
