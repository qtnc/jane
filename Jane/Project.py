import re
from pathlib import Path
from os import path

class Project:
	def __init__ (self, root):
		self.root=root
	
	def open(self):
		pass
	
	def getSpecificMenus(self):
		return ()

	
	def findFiles (self, fn, base=None):
		name, ext = path.splitext(fn)
		if base and not ext: pat  = '**/' + name + '*' + base.suffix
		else: pat = '**/' + fn
		result = list(self.root.glob(pat))
		if result: return result
		if fn.islower(): pat = '**/' + '*'.join(fn) + '*' + base.suffix
		else: pat = '**/' + '*'.join(re.findall(r'[A-Z][^A-Z]*', fn)) + '*' + base.suffix
		print('Pattern: ', pat)
		result = list(self.root.glob(pat))
		if result: return result
		return ()