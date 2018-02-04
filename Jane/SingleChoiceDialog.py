import wx, re, collections, collections.abc as abc
from DialogBase import DialogBase
from wxutils import LetterNavigable

Item = collections.namedtuple('Item', ('index', 'value', 'text'))

class SingleChoiceDialog(DialogBase):
	def __init__(self, parent, message, title, options, selection=0, *args, **kwargs):
		self.message = message
		self.options = makeItems(options)
		self.selection = selection
		super().__init__(parent=parent, title=title, *args, **kwargs)
	
	def initUI(self, sizer):
		sizer.Add(wx.StaticText(self, label=self.message), 1)
		self.lb = lb = self.createListBox()
		sizer.Add(lb, 1, wx.EXPAND)
		lb.SetSelection(self.selection)
		lb.SetFocus()
	
	def createListBox(self):
		return LetterNavigable(wx.ListBox(self, style = wx.LB_SINGLE | wx.LB_NEEDED_SB | wx.LB_HSCROLL, choices=[i.text for i in self.options]))
	
	def GetSelection (self):
		return self.lb.GetSelection()
	
	def GetSelectionValue(self):
		return self.options[self.GetSelection()].value
	
	def GetSelectionText(self):
		return self.options[self.GetSelection()].text


def makeItem (o):
	if isinstance(o,abc.Sequence) and len(o)==2: return (o[0], str(o[1]))
	else: return (o,str(o))

def makeItems (options):
	if isinstance(options, abc.Mapping): return tuple(Item(i, e[0], str(e[1])) for i, e in enumerate(options.items()))
	elif isinstance(options, abc.Sequence): return tuple(Item(i, *makeItem(e)) for i, e in enumerate(options))
	raise TypeError('mapping or sequence expected')
