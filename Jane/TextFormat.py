import os, re, ctypes

defaultEncoding = 'utf-8'
legacyEncoding = 'iso-8859-1'
if os.name=='nt':
	defaultEncoding = 'cp' + str(ctypes.windll.kernel32.GetACP())
	legacyEncoding = 'cp' + str(ctypes.windll.kernel32.GetOEMCP())

lineEndings = {
	0:'\r\n', '\r\n':0, 'crlf':'\r\n', 'dos':'\r\n',
	1:'\n', '\n':1, 'lf':'\n', 'unix':'\n',
	2:'\r', '\r':2, 'cr':'\r', 'mac':'\r'
}

encodings = {
	0:defaultEncoding, defaultEncoding:0,
	1:'utf-8', 'utf-8':1, 'utf8':'utf-8', 
	2:'utf-8-sig', 'utf-8-sig':2, 
	3:'utf-16-le', 'utf-16-le':3,
	4:'utf-16-be', 'utf-16-be':4,
	7:legacyEncoding, legacyEncoding:7
}

allEncodings = (
	'big5', 'big5hkscs', 
	'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 
	'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 
	'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125', 'cp1140', 
	'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 
	'euc_jis_2004', 'euc_jisx0213', 'euc_jp', 'euc_kr', 'gb2312', 'gb18030', 'gbk', 
	'hp-roman8', 'hz', 'idna', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3', 'iso2022_jp_2004', 'iso2022_jp_ext', 'iso2022_kr', 
	'iso8859-1', 'iso8859-2', 'iso8859-3', 'iso8859-4', 'iso8859-5', 'iso8859-6', 'iso8859-7', 'iso8859-8', 'iso8859-9', 'iso8859-10', 'iso8859-11', 'iso8859-13', 'iso8859-14', 'iso8859-15', 'iso8859-16', 
	'johab', 'koi8-r', 'koi8-t', 'koi8-u', 'kz1048', 
	'mac-arabic', 'mac-centeuro', 'mac-croatian', 'mac-cyrillic', 'mac-farsi', 'mac-greek', 'mac-iceland', 'mac-latin2', 'mac-roman', 'mac-romanian', 'mac-turkish', 
	'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'tis-620', 
	'utf-7', 'utf-8', 'utf-8-sig', 'utf-16-be', 'utf-16-le', 'utf-32-be', 'utf-32-le'
)

def rbol (s, r=re.compile(r'[^ \t]')): # real beginning of line
	m = r.search(s)
	return m.start() if m else len(s)

def detectLineEnding (data, reg=re.compile(rb'\r\n|\n|\r')):
	m = reg.search(data)
	return str(m[0], encoding='utf-8') if m else os.linesep

def detectIndent (data, reg=re.compile(rb'^([\t ]+)', re.M)):
	count=0
	indent = 32767
	for match in reg.finditer(data):
		s = match[1]
		if len(s)<=1 or b'\t' in s: return 0
		indent = min(indent, len(s))
		count+=1
		if count>64: break
	return indent if indent in range(2, 9) else 0

def detectEncoding (data):
	if data[0:3]==b'\xEF\xBB\xBF': return 'utf-8-sig'
	elif data[0:2]==b'\xEF': return 'utf-16-le'
	elif data[0:2]==b'\xFF\xEF': return 'utf-16-be'
	elif len(data)>=6 and data[1]==0 and data[3]==0 and data[5]==0: return 'utf-16-le'
	elif len(data)>=6 and data[0]==0 and data[2]==0 and data[4]==0: return 'utf-16-be'
	for m in re.finditer(b'[\x80-\xFF]+', data):
		s=m[0]; c=s[0]; l=len(s); i=m.start()
		if c<0xA0: return legacyEncoding
		elif c<0xC2 or c>=0xF0: return defaultEncoding
		elif c>=0xC2 and c<0xE0 and l!=2: return defaultEncoding
		elif c>0xE0 and c<0xF0 and l!=3: return defaultEncoding
		elif i>4096: return 'utf-8'
	return 'utf-8'

