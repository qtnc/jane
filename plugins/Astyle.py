import subprocess
from TextType import TextType, DefaultType

ASTYLE_PATH = app.config.get('astyle', 'path', fallback='astyle')
ASTYLE_OPTIONS = app.config.get('astyle', 'options', fallback='')
ONSAVE = app.config.getboolean('astyle', 'autoformatOnSave', fallback=False)
ONLOAD = app.config.getboolean('astyle', 'autoformatOnLoad', fallback=False)

@TextType('java', 'cs', 'c', 'cc', 'cpp', 'cxx', 'h', 'hh', 'hpp', 'hxx')
class Astyle(DefaultType):
	def onSave (self, text, doc):
		return self.autoformat(text, doc) if ONSAVE else text
	def onLoad (self, text, doc):
		return self.autoformat(text, doc) if ONLOAD else text
	def autoformat(self, text, doc):
		indent = '-t' if doc.indent==0 else '-s'+str(doc.indent)
		mode = 'c'
		for t in ('java', 'cs'):
			if doc and doc.file and doc.file.name.lower().endswith(t): mode=t
		proc = subprocess.run('"{0}" --mode={1} {2} {3}'.format(ASTYLE_PATH, mode, indent, ASTYLE_OPTIONS), encoding='utf-8', errors='replace', cwd=doc.file.parent if doc and doc.file else None, input=text, stdout=subprocess.PIPE, check=True, universal_newlines=True)
		return proc.stdout

