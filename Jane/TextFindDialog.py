import wx, re
from DialogBase import DialogBase

class RegexValidator(wx.Validator):
	def Clone(self):
		v = RegexValidator()
		v.SetWindow(self.GetWindow())
		return v
	def TransferToWindow(self):
		return True
	def TransferFromWindow(self):
		return True
	def Validate(self, parent):
		if not parent.regex.IsChecked(): return True
		field = self.GetWindow()
		try:
			reg = re.compile(field.GetValue())
		except re.error as err:
			wx.MessageBox(translate('regexerr') .format(err.msg, err.colno), parent.GetTitle(), wx.OK | wx.ICON_STOP, parent)
			field.SetSelection(err.colno, err.colno)
			field.SetFocus()
			return False
		else:
			return True

class RegexReplacementValidator(wx.Validator):
	def __init__(self, regf, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.regf=regf
	def Clone(self):
		v = RegexReplacementValidator(self.regf)
		v.SetWindow(self.GetWindow())
		return v
	def TransferToWindow(self):
		return True
	def TransferFromWindow(self):
		return True
	def Validate(self, parent):
		if not parent.regex.IsChecked(): return True
		field = self.GetWindow()
		try:
			re.sub(self.regf.GetValue(), field.GetValue(), '')
		except (re.error, ValueError, IndexError, KeyError) as err:
			wx.MessageBox(translate('regexerr2') .format(err.msg if hasattr(err,'msg') else err.args[0]), parent.GetTitle(), wx.OK | wx.ICON_STOP, parent)
			field.SetFocus()
			return False
		else:
			return True

class TextFindDialog(DialogBase):
	finds = []
	replaces = []
	findsr = []
	lastup = False
	
	def __init__(self, parent, replace=False, *args, **kwargs):
		self.hasReplace = replace
		super().__init__(parent=parent, title=translate('FindReplace' if replace else 'Find'), *args, **kwargs)
	
	def initUI(self, sizer):
		cls = type(self)
		grid = wx.FlexGridSizer(2)
		grid.Add(wx.StaticText(self, label=translate('findLbl')+':'))
		self.find = wx.ComboBox(self, choices=cls.finds, validator=RegexValidator())
		grid.Add(self.find, 1, wx.EXPAND)
		self.find.Bind(wx.EVT_COMBOBOX, self.onSelChange)
		if self.hasReplace:
			grid.Add(wx.StaticText(self, label=translate('replaceWith')+':'))
			self.replace = wx.ComboBox(self, choices=cls.replaces, validator=RegexReplacementValidator(self.find))
			grid.Add(self.replace, 1, wx.EXPAND)
		if not self.hasReplace:
			self.replace = None
			box = wx.StaticBoxSizer(wx.HORIZONTAL, self, translate('direction'))
			sb = box.GetStaticBox()
			self.up = wx.RadioButton(sb, label=translate('up'), style=wx.RB_GROUP)
			self.down = wx.RadioButton(sb, label=translate('down'))
			box.Add(self.up, 1, wx.EXPAND)
			box.Add(self.down, 1, wx.EXPAND)
			grid.Add(box, 1, wx.EXPAND)
		else:
			self.up = self.down = None
			grid.Add(wx.StaticText(self, label=''), 1, wx.EXPAND)
		box = wx.BoxSizer(wx.VERTICAL)
		self.regex = wx.CheckBox(self, label=translate('regularExpression'))
		self.icase = wx.CheckBox(self, label=translate('ignoreCase'))
		box.Add(self.regex, 1, wx.EXPAND)
		box.Add(self.icase, 1, wx.EXPAND)
		grid.Add(box, 1, wx.EXPAND)
		sizer.Add(grid, 1, wx.EXPAND)
		if len(cls.finds)>0: self.find.SetSelection(0); self.onSelChange()
		else: self.icase.SetValue(True)
		if cls.lastup and self.up: self.up.SetValue(True)
		elif self.down: self.down.SetValue(True)
		if self.replace and len(cls.replaces)>0: self.replace.SetSelection(0)
		self.find.SetFocus()
	
	def onSelChange(self, e=None):
		cls = type(self)
		i = self.find.GetSelection()
		if i<0 or i>=len(cls.finds): return
		regex, icase = cls.findsr[i]
		self.regex.SetValue(regex)
		self.icase.SetValue(icase)
	
	def ShowModal (self):
		result = super().ShowModal()
		if result!=wx.ID_OK: return result
		cls = type(self)
		cls.lastup = self.up and self.up.GetValue()
		find = self.find.GetValue()
		replace = self.replace.GetValue() if self.replace else None
		regex = self.regex.IsChecked()
		icase = self.icase.IsChecked()
		i = cls.finds.index(find) if find in cls.finds else -1
		if i>=0:
			del cls.finds[i]
			del cls.findsr[i]
		cls.finds.insert(0, find)
		cls.findsr.insert(0, (regex, icase))
		i = cls.replaces.index(replace) if replace and replace in cls.replaces else -1
		if i>=0: del cls.replaces[i]
		if replace: cls.replaces.insert(0, replace)
		return result
	
	def getFindRegex(self):
		val = self.find.GetValue()
		ign = re.I if self.icase.IsChecked() else 0
		if self.regex.IsChecked(): return re.compile(val, re.S | re.M | ign)
		else: return re.compile(re.escape(val), ign)
	
	def getReplacement(self):
		value = self.replace.GetValue()
		return value if self.regex.IsChecked() else value.replace('\\', '\\\\')
