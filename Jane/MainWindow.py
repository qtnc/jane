import wx, re
from pathlib import Path
from collections import OrderedDict
from Document import Document
from SingleChoiceDialog import SingleChoiceDialog
import MenuManager, DocumentFactory

ID_MARK = 4995
ID_GO_TO_MARK = 4996
ID_SELECT_TO_MARK = 4997
ID_FIND_NEXT = 4998
ID_FIND_PREV = 4999
ID_TEST = 9999


FILE_MENU = (
	('newDocument', wx.ID_NEW),
	('openDialog', wx.ID_OPEN),
	('runCommandDialog', wx.ID_EXECUTE),
	('reloadDocument', wx.ID_REVERT),
	('saveDocument', wx.ID_SAVE),
	('saveDocumentAs', wx.ID_SAVEAS),
	('closeDocument', wx.ID_CLOSE),
	('test', ID_TEST),
	('exit', wx.ID_EXIT)
)

EDIT_MENU = (
	('undo', wx.ID_UNDO),
	('redo', wx.ID_REDO),
	('copy', wx.ID_COPY),
	('cut',  wx.ID_CUT),
	('paste', wx.ID_PASTE),
	('selectAll', wx.ID_SELECTALL),
	('mark', ID_MARK),
	('goToMark', ID_GO_TO_MARK),
	('selectToMark', ID_SELECT_TO_MARK),
	('jumpToDialog', wx.ID_JUMP_TO),
	('findDialog', wx.ID_FIND),
	('findReplaceDialog', wx.ID_REPLACE),
	('findNext', ID_FIND_NEXT),
	 ('findPrev', ID_FIND_PREV)
)

class MainWindow(wx.Frame):
	@property
	def document (self):
		return self.documents[self.nbctl.GetSelection()]
	
	def __init__ (self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.documents = []
		self.documentsByPath = {}
		self.untitledCount = 0
		self.closing = False
		self.ignorePageChanged = False
		self.oldSelection = -1
	
	def initUI (self):
		table = []
		menubar = wx.MenuBar()
		file, edit, fmt, help = wx.Menu(), wx.Menu(), wx.Menu(), wx.Menu()
		MenuManager.addItems(file, table=table, items=FILE_MENU)
		MenuManager.addItems(edit, table=table, items=EDIT_MENU)
		MenuManager.addItem(help, 'about', wx.ID_ABOUT)
		menubar.Append(file, translate('fileMenu'))
		menubar.Append(edit, translate('editMenu'))
		menubar.Append(help, translate('helpMenu'))
		self.SetMenuBar(menubar)
		self.SetAcceleratorTable(wx.AcceleratorTable(table))
		status = self.CreateStatusBar()
		toolbar = self.CreateToolBar()
		self.nbctl = wx.Notebook(parent=self, style=wx.NB_TOP | wx.NB_MULTILINE)
		self.nbctl.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
		self.nbctl.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)
		self.Bind(wx.EVT_CLOSE, self.onClose, source=self)
		self.Bind(wx.EVT_ACTIVATE, self.onActivate, source=self)
	
	def addDocument (self, doc):
		self.documents.append(doc)
		if doc.file: self.documentsByPath[doc.file]=doc
		doc.open()
		doc.component = doc.createUI(self.nbctl)
		self.nbctl.AddPage(doc.component, text=doc.name, select=True)
		self.onPageChanged(self.nbctl)
	
	def getDocument (self, e=None):
		if e is None or isinstance(e,wx.Event):
			i = self.nbctl.GetSelection()
			return self.documents[i], i
		elif isinstance(e,int):
			return self.documents[e], e
		elif isinstance(e, Document):
			return e, self.documents.index(e)
		else:
			raise TypeError('int or Document expected')
	
	def closeDocument (self, e=None):
		doc, index = self.getDocument(e)
		if doc.savable and doc.isModified():
			re = wx.MessageBox(translate('closeConfirm') .format(doc.name), translate('Question'), wx.YES_NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_EXCLAMATION, self)
			if re==wx.CANCEL: return False
			elif re==wx.YES and not self.saveDocument(e): return False
		if hasattr(doc, 'close') and callable(doc.close) and not doc.close(): return False
		if len(self.documents)>1: self.nbctl.SetSelection(index+1 if index<len(self.documents)-1 else index -1)
		self.nbctl.DeletePage(index)
		del self.documents[index]
		if doc.file: del self.documentsByPath[doc.file]
		return True
	
	def closeAllDocuments (self, e=None):
		return all(self.closeDocument(i) for i in range(len(self.documents) -1, -1, -1))
	
	def runCommand (self, cmd, name=None):
		curdoc = self.document
		if curdoc: project=curdoc.project; cwd=curdoc.file.parent if curdoc.file else None
		else: cwd = project = None
		self.addDocument(DocumentFactory.newDocument(type='_subprocess', cmd=cmd, name=name, project=project, cwd=cwd))
	
	def runCommandDialog(self, e=None):
		cmd = wx.GetTextFromUser(translate('runcmddlgm'), translate('runcmddlgc'))
		if cmd: self.runCommand(cmd)
	
	def checkConcurrentModifications(self):
		self.closing=True
		for doc in self.documents:
			if doc.reloadable and doc.isConcurrentlyModified() and (not doc.isModified() or wx.YES==wx.MessageBox(translate('concurrentModificationM') .format(doc.name, app.name), translate('Question'), wx.YES_NO | wx.YES_DEFAULT | wx.ICON_EXCLAMATION, self)): doc.open(reloading=True)
		self.closing=False
	
	def saveDialog (self, file=None):
		with wx.FileDialog(parent=self, message=translate('FDSave'), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
			if file: fileDialog.SetPath(str(file))
			if fileDialog.ShowModal() == wx.ID_CANCEL: return None
			else: return Path(fileDialog.GetPath()).resolve()
	
	def saveDocumentAs (self, e=None):
		doc, index = self.getDocument(e)
		file = self.saveDialog(doc.file)
		if not file: return False
		if not doc.save(file): return False
		self.nbctl.SetPageText(index, doc.name)
		if index==self.nbctl.GetSelection(): self.updateWindowTitle(doc)
		return True
	
	def saveDocument (self, e=None):
		doc, index = self.getDocument(e)
		return doc.save() or self.saveDocumentAs(e)
	
	def openDialog (self, e=None):
		with wx.FileDialog(parent=self, message=translate('FDOpen'), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL: return
			else: self.openDocuments(fileDialog.GetPaths())
	
	def openDocuments (self, files):
		for file in files: self.openDocument(file)
	
	def openDocument (self, file, arg=None):
		if arg is None:
			i = file.find(':', 6)
			if i>=6: arg = file[i+1:]; file=file[:i]
		file = Path(file).resolve()
		if file in self.documentsByPath:
			doc = self.documentsByPath[file]
			self.nbctl.SetSelection(self.documents.index(doc))
			doc.jumpTo(arg)
		else:
			doc = DocumentFactory.openDocument(file)
			self.addDocument(doc)
			doc.jumpTo(arg)
	
	def reloadDocument(self, e=None):
		doc, index = self.getDocument(e)
		doc.open(reloading=True)
	
	def newDocument (self, e=None, type=None, name=None, file=None, data=None, *args, **kwargs):
		if not name and not file:
			self.untitledCount+=1
			name = translate('untitled').format(self.untitledCount)
		if file or data: doc = DocumentFactory.openDocument(file, name, data, *args, **kwargs)
		else:
			doc = DocumentFactory.newDocument(type, name, *args, **kwargs)
			if not doc.project and self.documents: doc.project = self.document.project
		self.addDocument(doc)
		return doc
	
	def paste(self, e=None):
		self.document.paste()
	
	def copy(self, e=None):
		self.document.copy()
	
	def cut(self, e=None):
		self.document.cut()
	
	def selectAll(self, e=None):
		self.document.selectAll()
	
	def undo(self, e=None):
		self.document.undo()
	
	def redo(self, e=None):
		self.document.redo()
	
	def findDialog(self, e=None):
		self.document.findDialog(self)
	
	def findReplaceDialog(self, e=None):
		self.document.findReplaceDialog(self)
	
	def findNext(self, e=None):
		self.document.findNext(self)
	
	def findPrev(self, e=None):
		self.document.findPrev(self)
	
	def jumpToDialog(self, e=None):
		dst = wx.GetTextFromUser(translate('JumpToM'), translate('JumpToT'), '', self)
		if dst: self.jumpTo(dst)
	
	def jumpTo(self, dst):
		if dst.startswith('/') or dst.startswith('\\') or re.match(r'^[a-zA-Z]:[\\/]', dst): return self.openDocument(dst) # absolute path
		if self.document.project:
			m = re.match(r'^(?![-\d])[-_\w\d.\\/]+', dst)
			if m:
				fn, arg = dst[:m.end()], dst[m.end():]
				files = self.document.project.findFiles(fn, self.document.file)
				if not files: file = None
				elif len(files)==1: file = files[0]
				else: i = self.showContextMenu(('{0} ({1})'.format(f.name, f.relative_to(self.document.project.root)) for f in files)); file = files[i] if i>=0 and i<len(files) else None
				if file: return self.openDocument(file, arg)
		return self.document.jumpTo(dst)
	
	def mark(self, e=None):
		self.document.mark()
	
	def goToMark(self, e=None):
		self.document.goToMark()
	
	def selectToMark(self, e=None):
		self.document.selectToMark()
	
	def about(self, e=None):
		wx.MessageBox(translate('aboutText') .format(app.name, app.version, 'Copyright \u00A9 2018, Quentin Cosendey (http://quentinc.net/)'), translate('about1') .format(app.name), wx.OK | wx.ICON_INFORMATION, self)
	
	def exit (self, e=None):
		self.Close()
	
	def test(self, e=None):
		scd = SingleChoiceDialog(win, 'Test message', 'Test title', ('One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve'))
		scd.Show()
	
	def updateWindowTitle (self, doc=None, modified=None):
		if not doc: doc = self.document
		if modified is None: modified = doc.isModified()
		self.SetTitle(translate('winTitle').format(name=doc.name, file=doc.file or doc.name, appName=app.name, mod='*' if modified else ''))
	
	def showContextMenu (self, options):
		menu = wx.Menu()
		for id, label in enumerate(options, 1): menu.Append(id, label)
		result = self.GetPopupMenuSelectionFromUser(menu)
		menu.Destroy()
		return result -1 if result>=1 else -1
	
	def onPageChanging(self, e):
		self.oldSelection = e.GetOldSelection()
		e.Skip()
	
	def onPageChanged (self, e):
		if self.ignorePageChanged: return
		selection = e.GetSelection()
		doc = self.documents[selection]
		oldDoc = self.documents[self.oldSelection] if self.oldSelection>=0 else None
		self.oldSelection = selection
		project, oldProject = doc.project, oldDoc.project if oldDoc else None
		self.updateWindowTitle(doc)
		menubar = self.GetMenuBar()
		docMenus = doc.getSpecificMenus()
		oldDocMenus = oldDoc.getSpecificMenus() if oldDoc else ()
		if oldDocMenus!=docMenus:
			for i in range(1+len(oldDocMenus), 1, -1): menubar.Remove(i)
			for i, it in enumerate(docMenus, 2): menubar.Insert(i, it[0], it[1])
		if oldProject!=project:
			projMenus = project.getSpecificMenus() if project else ()
			oldProjMenus = oldProject.getSpecificMenus() if oldProject else ()
			if oldProjMenus!=projMenus:
				pmIndex = 2 + len(docMenus)
				for i in range(pmIndex+len(oldProjMenus) -1, pmIndex -1, -1): menubar.Remove(i)
				for i, it in enumerate(projMenus, pmIndex): menubar.Insert(i, it[0], it[1])
		for name, id in EDIT_MENU: menubar.Enable(id, hasattr(doc, name) and callable(getattr(doc, name)) and doc.canDo(id))
		for name, id in FILE_MENU: menubar.Enable(id, doc.canDo(id))
		menubar.Refresh()
		doc.onFocus()
	
	def onActivate(self, e):
		if e.GetActive() and not self.closing: wx.CallAfter(self.checkConcurrentModifications)
		e.Skip()
	
	def onClose (self, e):
		self.closing=True
		if e.CanVeto() and not self.closeAllDocuments(): e.Veto(); self.closing=False; return False
		else: self.Destroy(); return True
