from TextFormat import rbol
import re
import utils

class DefaultType:
	def getLevel(self, line): return rbol(line)
	def getLevelCalc(self, direction): return self.getLevel
	def isBlankLine(self, line): return line.isspace() or not line
	def onEnter(self, line): pass
	def onLoad (self, text, doc): return text
	def onSave (self, text, doc): return text
	def onCharHook (self, key, mod, editor, document): pass

factories = []
types = {}

def getTextTypes (file, text):
	return [tt() for tt in (types.get(file.suffix[1:].lower() if file is not None else None, []) + list(filter(lambda f: f(file, text), factories)) or [DefaultType])]

# Intended to be used as annotation by plugins
def TextType (*suffixes):
	if len(suffixes)<=0: raise ValueError('Expected factory function or list of suffixes')
	elif len(suffixes)==1 and callable(suffixes[0]): factories.append(suffixes[0]); return suffixes[0]
	def addSuffixes (type):
		for suffix in suffixes:
			if suffix in types: types[suffix].append(type)
			else: types[suffix] = [type]
		return type
	return addSuffixes
