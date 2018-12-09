import os, time
import editorconfig
import Project

class Document:
	def __init__(self, file=None, name=None, project=None, props=None, reloadable=False, savable=True, readOnly=False):
		self.name=name
		self.file=file
		self.project = project
		self.props = props or {}
		self.modificationTime = -1
		self.reloadable = reloadable
		self.savable = savable
		self.readOnly=readOnly
		self.acceleratorTable = []
	
	def open(self, file=None, reloading=False):
		if reloading and not self.reloadable and not file: return False
		if file: self.file=file
		if not self.file: return False
		self.project = Project.getProjectOf(self.file)
		self.reloadable = True
		try: self.props = editorconfig.get_properties(self.file)
		except editorconfig.EditorConfigError: self.props = {}
		try: self.modificationTime = os.stat(self.file).st_mtime
		except (FileNotFoundError, OSError): self.modificationTime = -1
		return True
	
	def save(self, file):
		if not self.savable and not file: return False
		if not file: file=self.file
		if not file: return False
		self.file=file
		self.project = Project.getProjectOf(self.file)
		self.savable = True
		try: self.props = editorconfig.get_properties(self.file)
		except editorconfig.EditorConfigError: self.props = {}
		self.modificationTime = time.time()
		return True
	
	def isModified(self):
		return False
	
	def isConcurrentlyModified(self):
		try: return self.modificationTime>0 and os.stat(self.file).st_mtime > self.modificationTime
		except (FileNotFoundError, OSError): return False
	
	def jumpToDialog(self): return False
	def canDo (self, id): return True
	def getSpecificMenus(self): return ()
	def getEditMenuSpecificItems(self): return ()
	def getFileMenuSpecificItems(self): return ()
	
#	def getData(self):
#		raise ValueError('Unsupported operation')
