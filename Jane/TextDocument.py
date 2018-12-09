import wx, re, functools
import utils, TextFormat, TextType, MenuManager
from Document import Document
from TextEditor import TextEditor
from TextFindDialog import TextFindDialog
from SingleChoiceDialog import SingleChoiceDialog

class TextDocument(Document):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.encoding = app.config.get('text', 'encoding', fallback=TextFormat.defaultEncoding)
		self.lineEnding = TextFormat.lineEndings.get(app.config.get('text', 'lineEnding', fallback=-1), '\r\n')
		self.types = [TextType.DefaultType()]
		self.indent = app.config.getint('text', 'indentation', fallback=0)
		self.wrap = app.config.getboolean('text', 'autowrap', fallback=False)
		self.editor = None
	
	def getTextType(self, ttp):
		return utils.first(tt for tt in self.types if type(tt)==ttp)
	
	def createUI(self, parent):
		win.Bind(wx.EVT_MENU_RANGE, changeEncoding, id=ID_ENC_FIRST, id2=ID_ENC_LAST)
		win.Bind(wx.EVT_MENU_RANGE, changeLineEnding, id=ID_LE_FIRST, id2=ID_LE_LAST)
		win.Bind(wx.EVT_MENU_RANGE, changeIndent, id=ID_INDENT_TABS, id2=ID_INDENT_TABS+8)
		self.component = self.editor = TextEditor(parent, self, self.wrap)
		self.editor.SetEditable(not self.readOnly)
		if hasattr(self, '_text') and self._text: self.editor.SetValue(self._text); del self._text
		return self.component
	
	def open (self, file=None, reloading=False):
		if not super().open(file, reloading): return False
		data = None
		try: data = self.file.read_bytes()
		except (FileNotFoundError, OSError) as e: print('error: ', e); return False
		return self.setData (data, reloading)
	
	def setData (self, data, reloading=False):
		if not reloading:
			self.encoding = TextFormat.encodings.get(self.props['charset'], self.props['charset']) if 'charset' in self.props else TextFormat.detectEncoding(data)
			self.lineEnding = TextFormat.lineEndings[self.props['end_of_line']] if 'end_of_line' in self.props else TextFormat.detectLineEnding(data)
			if 'indent_style' in self.props:
				if self.props['indent_style']=='tab': self.indent=0
				elif 'indent_size' in self.props:
					if self.props['indent_size'].isdigit(): self.indent = int(self.props['indent_size'])
					elif 'tab_width' in self.props and self.props['tab_width'].isdigit(): self.indent = int(self.props['tab_width'])
			else: self.indent = TextFormat.detectIndent(data)
		text = str(data, encoding=self.encoding, errors='replace')
		if self.lineEnding!='\n': text = '\n'.join(text.split(self.lineEnding))
		if not reloading: self.types  = TextType.getTextTypes(self.file, text)
		text = functools.reduce(lambda tx, tp: tp.onLoad(tx, self), self.types, text)
		if self.editor:
			start, end = self.editor.GetSelection2()
			self.editor.SetValue(text)
			self.editor.SetSelection(start, end)
			self.editor.SetModified(False)
		else: self._text = text
		return True
	
	def getData(self):
		if 'charset' in self.props: self.encoding = TextFormat.encodings.get(self.props['charset'], self.props['charset'])
		if 'end_of_line' in self.props : self.lineEnding = TextFormat.lineEndings[self.props['end_of_line']]
		text = self.editor.GetValue()
		self.types = TextType.getTextTypes(self.file, text)
		text = functools.reduce(lambda tx, tp: tp.onSave(tx, self), self.types, text)
		if 'trim_trailing_whitespace' in self.props and self.props['trim_trailing_whitespace']=='true': text = re.compile(r'\s+$', re.M).sub('', text)
		if 'insert_final_newline' in self.props and self.props['insert_final_newline']=='true' and not text.endswith('\n'): text+='\n'
		if self.lineEnding!='\n': text = self.lineEnding.join(text.split('\n'))
		data = bytes(text, encoding=self.encoding, errors='replace')
		return data
	
	def save (self, file=None):
		if not super().save(file): return False
		data = self.getData()
		self.file.write_bytes(data)
		self.name=self.file.name
		self.editor.SetModified(False)
		return True
	
	def paste (self):
		if not self.readOnly: self.editor.Paste()
	
	def copy(self):
		self.editor.Copy()
	
	def cut(self):
		if not self.readOnly: self.editor.Cut()
	
	def selectAll (self):
		self.editor.SelectAll()
	
	def undo(self):
		if not self.readOnly: self.editor.Undo()
	
	def redo(self):
		if not self.readOnly: self.editor.Redo()
	
	def isModified(self):
		return self.editor.IsModified()
	
	def findDialog(self, parent):
		with TextFindDialog(parent) as tfd:
			if tfd.ShowModal() != wx.ID_OK: return False
			reg, up = tfd.getFindRegex(), tfd.up.GetValue()
			if up: return self.editor.findPrev(reg)
			else: return self.editor.findNext(reg)
	
	def findReplaceDialog(self, parent):
		if self.readOnly: return -2
		with TextFindDialog(parent, True) as tfd:
			if tfd.ShowModal() != wx.ID_OK: return -1
			count = self.editor.findReplace(tfd.getFindRegex(), tfd.getReplacement())
			win.SetStatusText(translate('replacementsMade').format(count))
			return count
	
	def findNext (self, parent):
		if TextEditor.findRegex is None: return self.findDialog(parent)
		else: return self.editor.findNext()
	
	def findPrev (self, parent):
		if TextEditor.findRegex is None: return self.findDialog(parent)
		else: return self.editor.findPrev()
	
	def jumpTo(self, arg):
		if not arg: return True
		m = re.match(r'^([:+-]?)(\d+)$', arg)
		if m:
			if not m[1] or m[1]==':': self.editor.SetInsertionPointXY(0, int(m[2]) -1); return True
			elif m[1]=='+': self.editor.SetInsertionPointXY(0, self.editor.GetLine()+int(m[2])); return True
			elif m[1]=='-': self.editor.SetInsertionPointXY(0, max(0, self.editor.GetLine() -int(m[2]))); return True
		m = re.match(r'^:?\[?(\d+)(\D)(\d+)\]?$', arg)
		if m:
			if m[2]=='-': self.editor.SetSelectionXY(0, int(m[1]) -1, 4096, int(m[3]) -1); return True
			else: self.editor.SetInsertionPointXY(int(m[3]) -1, int(m[1]) -1); return True
		m = re.match(r'^:?\[?(\d+)\D(\d+)\D(\d+)\D(\d+)\]?$', arg)
		if m: self.editor.SetSelectionXY( int(m[2]) -1, int(m[1]) -1, int(m[4]) -1, int(m[3]) -1); return True
		return False
	
	def mark(self):
		self.editor.mark()
	
	def goToMark(self):
		self.editor.goToMark()
	
	def selectToMark(self):
		self.editor.selectToMark()
	
	def setReadOnly(self, ro):
		self.readOnly=ro
		if self.editor: self.editor.SetEditable(not ro)
	
	def setEncoding (self, enc):
		self.encoding = enc if isinstance(enc,str) else TextFormat.encodings[enc]
	
	def setLineEnding (self, le):
		self.lineEnding = le if isinstance(le,str) else TextFormat.lineEndings[le]
	
	def setIndent (self, indent):
		oldIndent = self.indent
		self.indent=max(0, min(indent, 8))
		if self.editor and self.editor.HasSelection():
			indreg = re.compile(r'^\t' if oldIndent==0 else r'^ {' + str(oldIndent) + r'}', re.M)
			newIndent = '\t' if self.indent==0 else self.indent * ' '
			self.editor.findReplace(indreg, newIndent)
	
	def setWrap (self, wrap, parent):
		if self.wrap==wrap: return
		self.wrap=wrap
		value = self.editor.GetValue()
		start, end = self.editor.GetSelection()
		mod = self.editor.IsModified()
		cur = parent.GetSelection()
		i = parent.FindPage(self.component)
		parent.DeletePage(i)
		self.component = self.createUI(parent)
		self.editor.SetValue(value)
		self.editor.SetSelection(start, end)
		self.editor.SetModified(mod)
		parent.InsertPage(i, self.component, self.name, i==cur)
	
	def canDo(self, id):
		if self.readOnly and id in (wx.ID_SAVE, wx.ID_SAVEAS, wx.ID_REVERT, wx.ID_CUT, wx.ID_PASTE, wx.ID_UNDO, wx.ID_REDO, wx.ID_REPLACE): return False
		else: return True
	
	def onFocus(self):
		self.editor.SetFocus()
		self.editor.updateStatus()
		menubar = win.GetMenuBar()
		enci = TextFormat.encodings.get(self.encoding, -1)
		lei = TextFormat.lineEndings.get(self.lineEnding, -1)
		if enci>=0: menubar.Check(ID_ENC_FIRST+enci, True)
		if lei>=0: menubar.Check(ID_LE_FIRST+lei, True)
		menubar.Check(ID_INDENT_TABS+self.indent, True)
		menubar.Check(ID_AUTOWRAP, self.wrap)
		menubar.Check(ID_READONLY, self.readOnly)
		for id in (ID_READONLY, ID_AUTOWRAP): menubar.Enable(id, self.canDo(id))
	
	def getSpecificMenus(self):
		return [('formatMenu', FORMAT_MENU + utils.flatten((tt.getFormatMenuSpecificItems() for tt in self.types), tuple, 1))] + utils.flatten((tt.getSpecificMenus() for tt in self.types), list, 1)
	
	def getEditMenuSpecificItems(self):
		return utils.flatten((tt.getEditMenuSpecificItems() for tt in self.types), tuple, 1)
	
	def getFileMenuSpecificItems(self):
		return utils.flatten((tt.getFileMenuSpecificItems() for tt in self.types), tuple, 1)


def encodingDialog(e=None):
	lst = [(x, translate('enc-'+x.replace('_', '-').lower())) for x in TextFormat.allEncodings]
	with SingleChoiceDialog(win, translate('encodingDialogM'), translate('encodingDialogT'), lst) as sd:
		if sd.ShowModal() != wx.ID_OK: return
		enc = sd.GetSelectionValue()
		win.document.setEncoding(enc)

def changeEncoding (e):
	win.document.setEncoding(e.GetId() -ID_ENC_FIRST)

def changeLineEnding (e):
	win.document.setLineEnding(e.GetId() -ID_LE_FIRST)

def changeIndent (e):
	win.document.setIndent(e.GetId() -ID_INDENT_TABS)

def toggleAutoWrap(e=None):
	win.ignorePageChanged = True
	win.document.setWrap(not win.document.wrap, win.nbctl)
	win.document.onFocus()
	win.ignorePageChanged = False

def toggleReadOnly(e=None):
	win.document.setReadOnly(not win.document.readOnly)
	win.onPageChanged(win.nbctl)
	win.document.onFocus()


ID_ENC_DEFAULT = 6000
ID_ENC_UTF8 = 6001
ID_ENC_UTF8_BOM = 6002
ID_ENC_UTF16LE = 6003
ID_ENC_UTF16BE = 6004
ID_ENC_LEGACY_DEFAULT = 6007
ID_ENC_OTHER=6256
ID_INDENT_TABS = 6280
ID_LE_CRLF = 6290
ID_LE_LF = 6291
ID_LE_CR = 6292
ID_AUTOWRAP = 6279
ID_READONLY = 6278
ID_ENC_FIRST = ID_ENC_DEFAULT
ID_ENC_LAST = ID_ENC_OTHER -1
ID_LE_FIRST = ID_LE_CRLF
ID_LE_LAST = ID_LE_CR+1

ENCODING_MENU = (
	('enc-'+TextFormat.defaultEncoding, ID_ENC_DEFAULT, wx.ITEM_RADIO, True),
	('enc-utf-8', ID_ENC_UTF8 if TextFormat.defaultEncoding!='utf-8' else wx.ID_NONE, wx.ITEM_RADIO),
	('enc-utf-8-sig', ID_ENC_UTF8_BOM, wx.ITEM_RADIO),
	('enc-utf-16-le', ID_ENC_UTF16LE, wx.ITEM_RADIO),
	('enc-utf-16-be', ID_ENC_UTF16BE, wx.ITEM_RADIO),
	('enc-'+TextFormat.legacyEncoding, ID_ENC_LEGACY_DEFAULT, wx.ITEM_RADIO),
	(encodingDialog, ID_ENC_OTHER)
)

FORMAT_MENU = (
	('lineEnding', (
		('LE_CRLF', ID_LE_CRLF, wx.ITEM_RADIO, True),
		('LE_LF', ID_LE_LF, wx.ITEM_RADIO),
		('LE_CR',  ID_LE_CR, wx.ITEM_RADIO)
	)), ('encoding', ENCODING_MENU),
	('indentation', (
		('indentTabs', ID_INDENT_TABS, wx.ITEM_RADIO, True),
		*((('indentSpaces', i), ID_INDENT_TABS+i, wx.ITEM_RADIO) for i in range(2,9))
	)),
	(toggleAutoWrap, ID_AUTOWRAP, wx.ITEM_CHECK, False),
	(toggleReadOnly, ID_READONLY, wx.ITEM_CHECK, False)
)

