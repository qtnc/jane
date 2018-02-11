import re, wx
import utils
from TextFormat import rbol

def bellFalsy (x):
	if not x: wx.Bell()
	return x

def rsearch(reg, value, end, start=0, nth=-1):
		matches = []
		while True:
			m = reg.search(value, start, end)
			if m: matches.append(m); start = m.end()
			else: break
		try: return matches[nth]
		except IndexError: return None

class TextDeleted:
	POS_START, POS_END, SELECT_FORWARD, SELECT_BACKWARD = -1, -2, -3, -4
	def __init__(self, start, end, text, select):
		self.start, self.end, self.text, self.select = start, end, text, select
	def redo(self, editor):
		editor.Replace(self.start, self.end, '')
	def undo(self, editor):
		editor.Replace(self.start, self.start, self.text)
		if self.select==self.POS_START: editor.SetInsertionPoint(self.start)
		elif self.select==self.POS_END: editor.SetInsertionPoint(self.end)
		elif self.select==self.SELECT_FORWARD: editor.SetSelection(self.start, self.end)
		elif self.select==self.SELECT_BACKWARD: editor.SetSelection(self.end, self.start)
		else: editor.SetInsertionPoint(self.select)
	def join(self, state):
		if not isinstance(state, TextDeleted): return False
		if state.end==self.start:
			self.text = state.text + self.text
			self.start = state.start
			return True
		elif self.start == state.start:
			self.text += state.text
			self.end += (state.end -state.start)
			return True
		return False

class TextInserted:
	def __init__(self, pos, text, select=False):
		self.pos, self.text, self.select = pos, text, select
	def redo(self, editor):
		editor.Replace(self.pos, self.pos, self.text)
		if self.select: editor.SetSelection(self.pos, self.pos+len(self.text))
		else: editor.SetInsertionPoint(self.pos+len(self.text))
	def undo(self, editor):
		editor.Replace(self.pos, self.pos+len(self.text), '')
	def join(self, state):
		if isinstance(state, TextInserted) and state.pos == self.pos+len(self.text):
			self.text += state.text
			return True
		return False

class TextReplaced:
	POS_START, POS_END, SELECT_FORWARD, SELECT_BACKWARD = -1, -2, -3, -4
	def __init__(self, start, end, oldText, newText, select=-3):
		self.start, self.end, self.oldText, self.newText, self.select = start, end, oldText, newText, select
	def redo(self, editor):
		editor.Replace(self.start, self.start+len(self.oldText), self.newText)
		if self.select==self.SELECT_FORWARD: editor.SetSelection(self.start, self.start+len(self.newText))
		elif self.select==self.SELECT_BACKWARD: editor.SetSelection(self.start+len(self.newText), self.start)
		elif self.select==self.POS_END: editor.SetInsertionPoint(self.start+len(self.newText))
		elif self.select==self.POS_START: editor.SetInsertionPoint(self.start)
		else: raise ValueError('Invalid select value: ' +str(self.select))
	def undo(self, editor):
		editor.Replace(self.start, self.start+len(self.newText), self.oldText)
		if self.select==self.SELECT_FORWARD: editor.SetSelection(self.start, self.end)
		elif self.select==self.SELECT_BACKWARD: editor.SetSelection(self.end, self.start)
		elif self.select==self.POS_END: editor.SetInsertionPoint(self.end)
		elif self.select==self.POS_START: editor.SetInsertionPoint(self.start)
		else: raise ValueError('Invalid select value: ' +str(self.select))
	def join(self, state):
		return False

class TextEditor(wx.TextCtrl):
	findRegex = None
	
	def __init__(self, parent, doc, wrap=False):
		super().__init__(parent, style = wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_PROCESS_TAB | (0 if wrap else wx.TE_DONTWRAP))
		self.document = doc
		self.anchor = 0
		self.marker = 0
		self.undoPos = 0
		self.undos = []
		self.SetModified(False)
		self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
		self.Bind(wx.EVT_CHAR, self.onChar)
		self.Bind(wx.EVT_KEY_UP, self.onKeyUp)
		self.Bind(wx.EVT_LEFT_UP, self.onMouseUp)
		self.Bind(wx.EVT_RIGHT_UP, self.onMouseUp)
		self.Bind(wx.EVT_MIDDLE_UP, self.onMouseUp)
		self.Bind(wx.EVT_TEXT_PASTE, self.onPaste)
		self.Bind(wx.EVT_TEXT_COPY, self.onCopy)
		self.Bind(wx.EVT_TEXT_CUT, self.onCut)
	
	def GetLine(self):
		return self.PositionToXY(self.GetInsertionPoint())[2]
	
	def SetInsertionPointXY (self, x, y):
		pos = self.XYToPosition(max(0, min(x, self.GetLineLength(y))), y)
		if pos>=0: self.SetInsertionPoint(pos); return True
		return False
	
	def SetSelectionXY (self, x1, y1, x2, y2):
		start = self.XYToPosition(max(0, min(x1, self.GetLineLength(y1))), y1)
		end = self.XYToPosition(max(0, min(x2, self.GetLineLength(y2))), y2)
		if start>=0 and end>=0: self.SetSelection(start, end); return True
		return False
	
	def GetInsertionPointXY (self):
		_, col, li = self.PositionToXY(self.GetInsertionPoint())
		return (col, li)
	
	def GetSelectionXY (self):
		start, end = self.GetSelection()
		_, x1, y1 = self.PositionToXY(start)
		_, x2, y2 = self.PositionToXY(end)
		return (x1, y1, x2, y2)
	
	def HasSelection(self):
		start, end = self.GetSelection()
		return start!=end
	
	def SetSelection(self, start, end):
		super().SetSelection(start, end)
		self.anchor=start
	
	def GetSelection2(self):
		start, end = self.GetSelection()
		return (end, start) if end==self.anchor else (start, end)
	
	def GetSelectionDirection(self, start=None, end=None):
		if start is None or end is None: start, end = self.GetSelection()
		if start==end: return 0
		elif start==self.anchor: return 1
		elif end==self.anchor: return -1
		else: raise ValueError('Unknown selection direction state: selection={0}, {1}; anchor={2}'.format(start, end, self.anchor))
	
	def SelectAll(self):
		super().SelectAll()
		self.anchor=0
	
	def Undo(self):
		if self.undoPos<1 or self.undoPos>len(self.undos): wx.Bell(); return False
		self.undoPos-=1
		self.undos[self.undoPos].undo(self)
		return True
	
	def Redo(self):
		if self.undoPos>=len(self.undos): wx.Bell(); return False
		self.undos[self.undoPos].redo(self)
		self.undoPos+=1
	
	def pushUndoState (self, state, tryJoin=True):
		if self.undoPos<len(self.undos): del self.undos[self.undoPos:]
		if tryJoin and self.undoPos>0 and self.undoPos<=len(self.undos) and self.undos[self.undoPos -1].join(state): return
		self.undos.append(state)
		self.undoPos = len(self.undos)
		if len(self.undos) > 50: self.undos.pop(0)
	
	def _textInserted (self, text, tryJoin=True):
		start, end = self.GetSelection()
		if start!=end: self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), TextDeleted.SELECT_FORWARD if self.GetSelectionDirection(start, end)>0 else TextDeleted.SELECT_BACKWARD))
		self.pushUndoState(TextInserted(start, text, False), tryJoin)
	
	def updateStatus(self):
		start, end = self.GetSelection()
		_, sc, sl = self.PositionToXY(start)
		if start==end:
			last = max(1, self.GetLastPosition())
			self.anchor=start
			text = translate('txtStatus').format(sl+1, sc+1, round(100*start/last))
		else:
			_, ec, el = self.PositionToXY(end)
			if self.anchor==end: sc, sl, ec, el = ec, el, sc, sl
			text = translate('txtStatus2').format(sl+1, sc+1, el+1, ec+1)
		win.SetStatusText(text)
	
	def findNext (self, reg=None):
		cls = type(self)
		if reg is None: reg = cls.findRegex
		else: cls.findRegex = reg
		start = max(self.GetSelection())
		match = reg.search(self.GetValue(), start)
		if not match: wx.Bell(); return False
		self.SetSelection(match.start(), match.end())
		return True
	
	def findPrev (self, reg=None):
		cls = type(self)
		if reg is None: reg = cls.findRegex
		else: cls.findRegex = reg
		value = self.GetValue()
		end = min(self.GetSelection())
		match = rsearch(reg, value, end)
		if not match: wx.Bell(); return False
		self.SetSelection(match.start(), match.end())
		return True
	
	def findReplace (self, reg, repl):
		start, end = self.GetSelection()
		text = self.GetValue()
		if start==end:
			newText, count  = reg.subn(repl, text)
			self.pushUndoState(TextReplaced(0, self.GetLastPosition(), text, newText, TextReplaced.POS_START))
			self.SetValue(newText)
			self.SetModified(True)
			return count
		else:
			seldir = self.GetSelectionDirection(start, end)
			newText, count  = reg.subn(repl, text[start:end])
			self.pushUndoState(TextReplaced(start, end, text, newText, TextReplaced.SELECT_FORWARD if seldir>0 else TextReplaced.SELECT_BACKWARD))
			self.Replace(start, end, newText)
			if seldir>0: self.SetSelection(start, start+len(newText))
			else: self.SetSelection(start+len(newText), start)
			self.SetModified(True)
			return count
	
	def goToNextParagraph(self, select=False, reg=re.compile(r'\n\s*?\n')):
		anchor, pos = self.GetSelection2()
		if pos>=self.GetLastPosition(): return False
		m = reg.search(self.GetValue(), pos)
		pos = m.end()+1 if m else self.GetLastPosition()
		if select: self.SetSelection(anchor, max(0, pos -1))
		else: self.SetInsertionPoint(max(0, pos -1))
		return True
	
	def goToPrevParagraph(self, select=False, reg=re.compile(r'\n\s*?\n')):
		anchor, pos = self.GetSelection2()
		if pos<=0: return False
		m = rsearch(reg, self.GetValue(), pos, nth=-2)
		pos = m.end()+1 if m else 0
		if select: self.SetSelection(anchor, max(0, pos -1))
		else: self.SetInsertionPoint(max(0, pos -1))
		return True
	
	def goToInnerIndent(self, select=False):
		getLevel = utils.first(t.getLevelCalc(1) for t in self.document.types)
		anchor, pos = self.GetSelection2()
		_, __, li = self.PositionToXY(pos)
		_, __, nl = self.PositionToXY(self.GetLastPosition())
		curline = self.GetLineText(li)
		curLevel = getLevel(curline)
		nextLine = self.GetLineText(li+1)
		nextLevel = getLevel(nextLine)
		if nextLevel<=curLevel or li>=nl: return False
		if select: self.SetSelection(anchor, self.XYToPosition(len(nextLine), li+1))
		else: self.SetInsertionPoint(self.XYToPosition(rbol(nextLine), li+1))
		return True
	
	def goToOuterIndent (self, select=False):
		getLevel, isBlankLine  = utils.first((t.getLevelCalc(-1), t.isBlankLine) for t in self.document.types)
		anchor, pos = self.GetSelection2()
		_, __, li = self.PositionToXY(pos)
		if li<=0: return False
		curline = self.GetLineText(li)
		curLevel = getLevel(curline)
		level = curLevel
		while li>=1:
			li-=1
			line = self.GetLineText(li)
			level = getLevel(line)
			if level<curLevel and not isBlankLine(line): break
		if select: self.SetSelection(anchor, self.XYToPosition(0, li))
		else: self.SetInsertionPoint(self.XYToPosition(rbol(line), li))
		return True

	def goToSameIndent (self, direction=1, select=False):
		getLevel, isBlankLine  = utils.first((t.getLevelCalc(direction), t.isBlankLine) for t in self.document.types)
		anchor, pos = self.GetSelection2()
		_, __, li = self.PositionToXY(pos)
		_, __, nl = self.PositionToXY(self.GetLastPosition())
		curline = self.GetLineText(li)
		curLevel = getLevel(curline)
		level = curLevel
		if li+direction<0 or li+direction>nl: return False
		while li>=0 and li<=nl:
			li+=direction
			line = self.GetLineText(li)
			level = getLevel(line)
			if level<curLevel: return False
			elif level==curLevel:
				if isBlankLine(line): continue
				else: break
		if select: self.SetSelection(anchor, self.XYToPosition(self.GetLineLength(li) if direction>=1 else 0, li))
		else: self.SetInsertionPoint(self.XYToPosition(rbol(line), li))
		return True
	
	def goToLastSameIndent (self, direction=1, select=False):
		count=0
		while self.goToSameIndent(direction, select): count+=1
		return count>0
	
	def mark (self):
		self.marker = self.GetInsertionPoint()
	
	def goToMark(self):
		self.SetInsertionPoint(self.marker)
	
	def selectToMark (self):
		self.SetSelection(self.anchor, self.marker)
	
	def onKeyUp (self, e):
		self.updateStatus()
		e.Skip()
	
	def onMouseUp(self, e):
		self.updateStatus()
		e.Skip()
	
	def onCharHook (self, e):
		key, mod = e.GetKeyCode(), e.GetModifiers()
		if key==wx.WXK_RETURN and mod==wx.MOD_NONE and not self.document.readOnly:
			self.onEnter()
		elif key==wx.WXK_RETURN and mod==wx.MOD_SHIFT and not self.document.readOnly:
			self.onEnter(1)
		elif key==wx.WXK_RETURN and mod==wx.MOD_CONTROL|wx.MOD_SHIFT and not self.document.readOnly:
			self.onEnter(-1)
		elif key==wx.WXK_RETURN and mod==wx.MOD_CONTROL:
			self.onCtrlEnter()
		elif key==wx.WXK_TAB and mod==wx.MOD_NONE and not self.document.readOnly:
			self.onTab()
		elif key==wx.WXK_TAB and mod==wx.MOD_SHIFT and not self.document.readOnly:
			self.onShiftTab()
		elif key==wx.WXK_BACK and mod==wx.MOD_NONE and not self.document.readOnly:
			if not self.onBackspace(): e.Skip()
		elif key==wx.WXK_DELETE and mod==wx.MOD_NONE and not self.document.readOnly:
			if not self.onDelete(): e.Skip()
		elif key==wx.WXK_HOME:
			if mod==wx.MOD_NONE: self.onHome()
			elif mod==wx.MOD_ALT: bellFalsy( self.goToLastSameIndent(direction=-1))
			elif mod==wx.MOD_ALT | wx.MOD_SHIFT: bellFalsy(self.goToLastSameIndent(direction=-1, select=True))
			else: e.Skip()
		elif key==wx.WXK_END:
			if mod==wx.MOD_SHIFT: self.onShiftEnd()
			elif mod==wx.MOD_SHIFT|wx.MOD_CONTROL: self.onCtrlShiftEnd()
			elif mod==wx.MOD_ALT: bellFalsy(self.goToLastSameIndent())
			elif mod==wx.MOD_ALT | wx.MOD_SHIFT: bellFalsy(self.goToLastSameIndent(select=True))
			else: e.Skip()
		elif key==wx.WXK_DOWN:
			if mod==wx.MOD_CONTROL: bellFalsy(self.goToNextParagraph())
			elif mod==wx.MOD_CONTROL | wx.MOD_SHIFT: bellFalsy(self.goToNextParagraph(True))
			elif mod==wx.MOD_ALT: bellFalsy(self.goToSameIndent())
			elif mod==wx.MOD_ALT | wx.MOD_SHIFT: bellFalsy(self.goToSameIndent(select=True))
			else: e.Skip()
		elif key==wx.WXK_UP:
			if mod==wx.MOD_CONTROL: bellFalsy(self.goToPrevParagraph())
			elif mod==wx.MOD_CONTROL | wx.MOD_SHIFT: bellFalsy(self.goToPrevParagraph(True))
			elif mod==wx.MOD_ALT: bellFalsy(self.goToSameIndent(direction=-1))
			elif mod==wx.MOD_ALT | wx.MOD_SHIFT: bellFalsy(self.goToSameIndent(-1, True))
			else: e.Skip()
		elif key==wx.WXK_RIGHT:
			if mod==wx.MOD_ALT: bellFalsy(self.goToInnerIndent())
			elif mod==wx.MOD_ALT | wx.MOD_SHIFT: bellFalsy(self.goToInnerIndent(True))
			else: e.Skip()
		elif key==wx.WXK_LEFT:
			if mod==wx.MOD_ALT: bellFalsy(self.goToOuterIndent())
			elif mod==wx.MOD_ALT | wx.MOD_SHIFT: bellFalsy(self.goToOuterIndent(True))
			else: e.Skip()
		elif utils.firstTruthy(t.onCharHook(key, mod, self, self.document) for t in self.document.types): e.Skip()
		else: e.Skip()
	
	def onChar(self, e):
		ch = e.GetUnicodeKey()
		if ch!=wx.WXK_NONE and ch!=8 and not self.document.readOnly: self._textInserted(chr(ch))
		if ch==wx.WXK_NONE or not self.document.readOnly: e.Skip()
	
	def onEnter(self, indent=None):
		line = self.GetLineText(self.GetLine())
		i = rbol(line)
		if indent is None: indent = utils.first((t.onEnter(line) for t in self.document.types), default=0)
		if indent<0: i = max(0, i - abs(indent) * max(1, self.document.indent))
		text = '\n' + line[:i]
		if indent>0: text += indent * ('\t' if self.document.indent<=0 else self.document.indent * ' ')
		self._textInserted(text, False)
		self.WriteText(text)
	
	def onHome(self):
		pos = self.GetInsertionPoint()
		_, col, li = self.PositionToXY(pos)
		line = self.GetLineText(li)
		i = rbol(line)
		self.SetInsertionPoint(self.XYToPosition(0 if col==i else i, li))
	
	def onShiftEnd(self):
		li = self.GetLine()
		llen = self.GetLineLength(li)
		end = self.XYToPosition(llen, li)
		self.SetSelection(self.anchor, end)
	
	def onCtrlShiftEnd(self):
		pos = self.GetLastPosition()
		self.SetSelection(self.anchor, pos)
	
	def onCtrlEnter(self):
		pos = self.GetInsertionPoint()
		_, col, li = self.PositionToXY(pos)
		line = self.GetLineText(li)
		last = 0
		for match in re.finditer(r'\b\S+\b', line):
			if col in range(*match.span()): return bellFalsy(win.jumpTo(match[0]))
		return bellFalsy(False)

	
	def onTab(self):
		start, end = self.GetSelection()
		_, __, sl = self.PositionToXY(start)
		_, __, el = self.PositionToXY(end)
		sp = self.XYToPosition(0, sl)
		ep = self.XYToPosition(0, el) + self.GetLineLength(el)
		text = self.GetRange(sp, ep)
		indent = '\t' if self.document.indent==0 else self.document.indent * ' '
		newText = re.compile(r'^', re.M).sub(indent, text)
		self.Replace(sp, ep, newText)
		if start==end:
			self.pushUndoState(TextReplaced(sp, start, text, newText, TextReplaced.POS_END))
			self.SetInsertionPoint(start + len(indent))
		else:
			self.pushUndoState(TextReplaced(sp, ep, text, newText, TextReplaced.SELECT_FORWARD if self.GetSelectionDirection()>0 else TextReplaced.SELECT_BACKWARD))
			self.SetSelection(sp, sp+len(text))
	
	def onShiftTab(self):
		start, end = self.GetSelection()
		indent = '\t' if self.document.indent==0 else self.document.indent * ' '
		_, __, sl = self.PositionToXY(start)
		_, __, el = self.PositionToXY(end)
		sp = self.XYToPosition(0, sl)
		ep = self.XYToPosition(0, el) + self.GetLineLength(el)
		text = self.GetRange(sp, ep)
		newText = re.compile(r'^' + indent, re.M).sub('', text)
		self.Replace(sp, ep, newText)
		if start==end:
			self.pushUndoState(TextReplaced(sp, start, text, newText, TextReplaced.POS_END))
			self.SetInsertionPoint(max(0, start -len(indent)))
		else:
			self.pushUndoState(TextReplaced(sp, ep, text, newText, TextReplaced.SELECT_FORWARD if self.GetSelectionDirection()>0 else TextReplaced.SELECT_BACKWARD))
			self.SetSelection(sp, sp+len(newText))
	
	def onBackspace(self):
		start, end = self.GetSelection()
		if start!=end:
			self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), TextDeleted.SELECT_FORWARD if self.GetSelectionDirection(start, end)>0 else TextDeleted.SELECT_BACKWARD))
			return False
		_, col, li = self.PositionToXY(start)
		line = self.GetLineText(li)
		bol = rbol(line)
		if col==bol and li>0:
			if app.config.get('text', 'onBackspaceInIndent', fallback=None)=='unindent' and col>=max(1, self.document.indent): start, end = max(0, start - max(1, self.document.indent)), start
			else: start, end = max(0, start -bol -1), start
			self.SetSelection(start, end)
		elif col<=bol:
			wx.Bell()
			return True
		else:
			start, end = max(0, start -1), start
		self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), TextDeleted.POS_START))
		return False
	
	def onDelete(self):
		start, end = self.GetSelection()
		if start!=end:
			self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), TextDeleted.SELECT_FORWARD if self.GetSelectionDirection(start, end)>0 else TextDeleted.SELECT_BACKWARD))
			return False
		deletedChar = self.GetRange(start, start+1)
		if deletedChar!='\n':
			self.pushUndoState(TextDeleted(start, start+1, deletedChar, TextDeleted.POS_END))
			return False
		_, __, li = self.PositionToXY(start)
		nextLine = self.GetLineText(li+1)
		bol = rbol(nextLine)
		if bol>0: 
			end = self.XYToPosition(bol, li+1)
			self.SetSelection(start, end)
		self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), TextDeleted.POS_END))
		return False
	
	def onPaste (self, e=None):
		text = app.GetClipboardText()
		if text is None:
			files = app.GetClipboardFiles()
			if files: text = '\n'.join(str(f) for f in files)
		if text is None: return bellFalsy(False)
		curline = self.GetLineText(self.GetLine())
		curbol = rbol(curline)
		lines = text.splitlines()
		bol = min(rbol(l) for l in lines)
		newText = '\n'.join(curline[:curbol] + l[bol:] if i else l[bol:] for i, l in enumerate(lines))
		self._textInserted(newText)
		self.WriteText(newText)
	
	def onCopy (self, e=None):
		start, end = self.GetSelection()
		if start==end: app.SetClipboardText(self.GetLineText(self.GetLine())); return True
		_, __, sl = self.PositionToXY(start)
		_, __, el = self.PositionToXY(end)
		if sl==el: e.Skip(); return False
		lstart = self.XYToPosition(0, sl)
		line = self.GetLineText(sl)
		bol = rbol(line)
		text = line[:bol] + self.GetRange(max(start, lstart+bol), end)
		app.SetClipboardText(text)
		return True
	
	def onCut (self, e=None):
		start, end = self.GetSelection()
		if start==end:
			li = self.GetLine()
			start = self.XYToPosition(0, li)
			end = start + self.GetLineLength(li) + 1
			self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), start))
			self.SetSelection(start, end)
		else:
			self.pushUndoState(TextDeleted(start, end, self.GetRange(start, end), TextDeleted.SELECT_FORWARD if self.GetSelectionDirection(start, end)>0 else TextDeleted.SELECT_BACKWARD))
		if self.onCopy(e): self.Replace(start, end, '')
