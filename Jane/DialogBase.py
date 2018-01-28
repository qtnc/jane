import wx

class DialogBase(wx.Dialog):
	def __init__(self, buttons = wx.OK | wx.CANCEL, *args, **kwargs):
		super().__init__(*args, **kwargs)
		topSizer = wx.BoxSizer(wx.VERTICAL)
		buttonsPane = self.CreateButtonSizer(buttons)
		self.initUI(topSizer)
		topSizer.Add(buttonsPane)
		self.SetSizerAndFit(topSizer)
	
	def initUI (self, sizer):
		pass