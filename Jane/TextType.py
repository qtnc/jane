from TextFormat import rbol
import re
import utils

class DefaultType:
	def getLevel(self, line): return rbol(line)
	def getLevelCalc(self, direction): return self.getLevel
	def onEnter(self, line): return 0
	def onCharHook (self, key, mod, editor, document): pass

class PythonType(DefaultType):
	def onEnter(self, line):
		return 1 if line.endswith(':') else 0

class CLikeType:
	def __init__(self):
		self.direction=0
		self.level=0
	def countOpens (self, line):
		return line.count('{')
	def countCloses(self, line):
		return line.count('}')
	def onEnter(self, line):
		return self.countOpens(line) - self.countCloses(line)
	def getLevel(self, line):
		opens, closes = self.countOpens(line), self.countCloses(line)
		level = self.level
		self.level += self.direction * (opens-closes)
		return min(level, self.level)
	def getLevelCalc(self, direction):
		self.direction=direction
		self.level=0
		return self.getLevel

class XMLType(CLikeType):
	def countOpens(self, line, reg=re.compile(r'<(?!/).*?(?<!/)>')):	
		count = len(reg.findall(line))
		return count
	def countCloses(self, line, reg=re.compile(r'</.*?>')):	
		count = len(reg.findall(line))
		return count

factories = []
types = {}
for type, suffixes in {
	CLikeType: ('c', 'cc', 'cpp', 'cxx', 'h', 'hh', 'hpp', 'hxx', 'tpp', 'java', 'php', 'pl', 'js', 'cs', 'css', 'less', 'sass', 'scss'), # C-like languages with {} blocks and // or /* comments
	PythonType: ('py', ), # Python 
	XMLType: ('xml', 'htm', 'html', 'xhtml', 'hta', 'xsd', 'xsl', 'svg') # XML-based languages
}.items():
	for suffix in suffixes: types[suffix]=type

def getTextType (file, text):
	tt = types.get(file.suffix[1:].lower() if file is not None else None, None)
	if not tt: tt = utils.first((f(file, text) for f in factories), default=DefaultType)
	return tt()


# Intended to be used as annotation by plugins
def TextType (*suffixes):
	if len(suffixes)<=0: raise ValueError('Expected factory function or list of suffixes')
	elif len(suffixes)==1 and callable(suffixes[0]): factories.append(suffixes[0]); return suffixes[0]
	def addSuffixes (type):
		for suffix in suffixes: types[suffix]=type
		return type
	return addSuffixes
