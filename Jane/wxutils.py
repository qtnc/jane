import wx, time, re, itertools

def LetterNavigable(ctl):
	ctl.input = ''
	ctl.time = 0
	ctl.Bind(wx.EVT_CHAR, letternavOnChar)
	return ctl

def letternavOnChar(e):
	ch = e.GetUnicodeKey()
	if ch==wx.WXK_NONE or ch<33: return e.Skip()
	ctl = e.GetEventObject()
	curtime = time.monotonic()
	if curtime-ctl.time>0.4: ctl.input=''
	ctl.input += chr(ch)
	ctl.time=curtime
	reg = re.compile(r'\b' + re.escape(ctl.input), re.I)
	pos = ctl.GetSelection()
	newPos = -1
	if len(ctl.input)<=1: pos+=1
	for i in itertools.chain(range(pos, ctl.GetCount()), range(0,pos)):
		str = ctl.GetString(i)
		if reg.search(str): newPos=i; break
	if newPos<0: wx.Bell()
	elif newPos!=pos: ctl.SetSelection(newPos)
