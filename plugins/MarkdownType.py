import wx, re
from TextType import TextType, DefaultType

@TextType('md')
class MarkdownType(DefaultType):
	def onCharHook(self, key, mod, editor, doc):
		if not doc.readOnly: return False
		elif mod!=wx.MOD_SHIFT and mod!=wx.MOD_NONE: return False
		pred = keys.get(key, None)
		if pred: return goTo(editor, -1 if mod==wx.MOD_SHIFT else 1, pred)

def goTo (editor, dir, pred):
	_, __, li = editor.PositionToXY(editor.GetInsertionPoint())
	_, __, nl = editor.PositionToXY(editor.GetLastPosition())
	if pred(editor.GetLineText(li)):
		while li>=0 and li<=nl and pred(editor.GetLineText(li)): li+=dir
	while li>=0 and li<=nl and not pred(editor.GetLineText(li)): li+=dir
	pos = editor.XYToPosition(0, li)
	editor.SetInsertionPoint(pos)
	return pred(editor.GetLineText(li))

def match (pat, opt=0):
	return lambda s: re.match(pat, s, opt)

keys = {
	72: match(r'^#'),
	49: match(r'^#(?!#)'),
	50: match(r'^##(?!#)'),
	51: match(r'^###(?!#)'),
	52: match(r'^####(?!#)'),
	53: match(r'^#####(?!#)'),
	81: match(r'^>'),
	76: match(r'^([-+*]|\d+\.)\s'),
	84: match(r'^\|?(?:[^|]+\|)+[^|]+\|?$')
}
			