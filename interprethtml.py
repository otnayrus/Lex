import re
from tabulate import tabulate

cm = 0
box = []
t = []

class Token:
	def __init__(self,string,tipe):
		self.htmlentities = string
		self.type = tipe;

def saring(line):
	global cm
	global t
	re_comment_open = re.compile("(.*)?(?=<!--)(<!--)([^\n]*)")
	re_comment_inline = re.compile("(.*)?(?=<!--)(<!--)(.*)(-->)([^\n]*)")
	re_comment_close = re.compile("(.*)?(?=-->)(-->)([^\n]*)")
	t_comment_open = re_comment_open.findall(line)
	t_comment_inline = re_comment_inline.findall(line)
	t_comment_close = re_comment_close.findall(line)
	
	if t_comment_inline :
		if(t_comment_inline[0][0] != '') : 
			bedah(t_comment_inline[0][0])
		t.append(Token(''.join(map(str,t_comment_inline[0][1])),"COMMENT_BEGIN_TAG"))
		t.append(Token(''.join(map(str,t_comment_inline[0][2])),"COMMENT_SECTION"))
		t.append(Token(''.join(map(str,t_comment_inline[0][3])),"COMMENT_END_TAG"))
		if(t_comment_inline[0][4] != '') : 
			bedah(t_comment_inline[0][4])
	elif t_comment_open :
		if(t_comment_open[0][0] != '') : 
			bedah(t_comment_open[0][0])
		t.append(Token(''.join(map(str,t_comment_open[0][1])),"COMMENT_BEGIN_TAG"))
		if(t_comment_open[0][2] != '\n') :
			t.append(Token(''.join(map(str,t_comment_open[0][2])),"COMMENT_SECTION"))
		cm += 1
	elif t_comment_close :
		if(t_comment_close[0][0] != '\n') :
			t.append(Token(''.join(map(str,t_comment_close[0][0])),"COMMENT_SECTION"))
		t.append(Token(''.join(map(str,t_comment_close[0][1])),"COMMENT_CLOSE_TAG"))
		if(t_comment_close[0][2] != '') : 
			bedah(t_comment_close[0][2])
		cm -= 1
		if cm < 0 : cm = 0
	elif cm > 0 :
		t.append(Token(line,"COMMENT_SECTION"))
	
	if cm == 0 and t_comment_inline == []: 
		bedah(line)
		
	if t : box.append(t)
	t = []
	
	
def bedah(string):
	global box
	global t
	d = '"'
	re_open_tag = re.compile("""(<([a-z0-9]+)([a-zA-Z0-9 '",.-_#]*?)>)""")
	re_close_tag = re.compile("""(</([a-z0-9]+)(?!\/)>)""")
	re_self_tag = re.compile("""(<([a-z0-9]+)([a-zA-Z0-9 ='",.\-_:/#]*?)\/>)""")
	re_attr = re.compile("""(\S+)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?""")
	re_doctype = re.compile("<!.* html>")
	re_raw = re.compile(">[^><]+<")
	re_any = re.compile(".+")
	
	t_doctype = re_doctype.findall(string)
	t_open_tag = re_open_tag.findall(string)
	t_close_tag = re_close_tag.findall(string)
	t_self_tag = re_self_tag.findall(string)
	t_raw = re_raw.findall(string)
	t_any = []
	if t_doctype == [] and t_open_tag == [] and t_close_tag == [] and t_self_tag == [] and t_raw == [] :
		t_any = re_any.findall(string)
	
	if t_doctype :
		t.append(Token(''.join(map(str,t_doctype[0])),"TAG_DOCTYPE"))
	if t_open_tag :
		for tags in t_open_tag :
			t.append(Token(tags[0], "OPEN_TAG"))
			if tags[2] != '':
				t_attr = re_attr.findall(tags[0])
				for a in t_attr:
					t.append(Token(''.join(map(str,a[0])), "ATTR_NAME"))
					t.append(Token(''.join(map(str,a[1])), "ATTR_VALUE"))
	if t_raw :
		for tags in t_raw:
			t.append(Token(''.join(map(str,tags))[1:-1],"RAW"))	
	if t_close_tag :
		for tags in t_close_tag :
			t.append(Token(tags[0], "CLOSE_TAG"))
	if t_self_tag :
		for tags in t_self_tag :
			t.append(Token(tags[0], "SELF_TAG"))
			if tags[2] != '':
				t_attr = re_attr.findall(tags[0])
				for a in t_attr:
					t.append(Token(''.join(map(str,a[0])), "ATTR_NAME"))
					t.append(Token(''.join(map(str,a[1])), "ATTR_VALUE"))
	if t_any :
		t.append(Token(t_any[0], "UNKNOWN_DATA"))
	
	box.append(t)
	t = []
	
def printout():
	global box
	for tokens in box:
		r = [['Token','Type']]
		for i in tokens:
			r.append([i.htmlentities,i.type])
		print(tabulate(r))
		print()
		
namafile = input('Masukkan nama file : ');		
f = open(namafile,'r')
for line in f:
	if line == '\n' : continue
	saring(line)
f.close()
printout()
