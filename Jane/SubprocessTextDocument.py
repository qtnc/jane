import wx, os, subprocess, time, collections
import utils, TextFormat
from threading import Thread
from TextDocument import TextDocument

class SubprocessTextDocument(TextDocument):
	def __init__(self, name=None, cmd=None, cwd=None, proc=None, input=None, output=None, *args, **kwargs):
		if name is None: name=cmd
		super().__init__(*args, name=name, readOnly=True, **kwargs)
		self.input = None
		self.cmd=cmd
		self.cwd=cwd
		self.proc = proc or utils.Object(stdout=input, stdin=output)
		self.lines = collections.deque()
		Thread(target=self.run, daemon=True).start()
	
	def createUI(self, parent):
		panel = wx.Panel(parent)
		editor = super().createUI(panel)
		self.input = wx.TextCtrl(panel, style = wx.TE_LEFT | wx.HSCROLL | wx.TE_PROCESS_ENTER)
		self.input.Bind(wx.EVT_TEXT_ENTER, self.doInput)
		self.input.Enable(False)
		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(editor, 1, wx.EXPAND)
		box.Add(self.input)
		panel.SetSizer(box)
		return panel
	
	def run(self):
		while not self.editor or not self.input: time.sleep(0.01)
		if self.cmd: self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=self.cwd, encoding=TextFormat.defaultEncoding, errors='replace')
		if self.proc and hasattr(self.proc, 'wait'): Thread(target=self.wait, daemon=True).start()
		if self.input and self.proc and hasattr(self.proc, 'stdout') and self.proc.stdout and not self.proc.stdout.closed: wx.CallAfter(lambda: self.input.Enable(True))
		while self.proc:
			line = self.proc.stdout.readline()
			if not line: time.sleep(0.01); continue
			self.lines.append(line)
			wx.CallAfter(lambda: self.append(self.lines.popleft()))
	
	def wait(self):
		exitCode = self.proc.wait()
		wx.CallAfter(lambda: self.append(translate('subprocessExit').format(exitCode)))
		if self.proc and hasattr(self.proc, 'terminate'): self.proc.terminate()
		time.sleep(1)
		if self.input: self.input.Enable(False)
		self.proc = self.input = None

	def close (self):
		if self.proc and hasattr(self.proc, 'terminate'): self.proc.terminate()
		self.proc = self.input = None
		return True
	
	def append(self, text):
		if not self.proc: return
		start, end = self.editor.GetSelection2()
		last = self.editor.GetLastPosition()
		self.editor.Replace(last, last, text)
		self.editor.SetSelection(start, end)
	
	def doInput(self, e=None):
		text = self.input.GetValue()
		self.input.SetValue('')
		if not self.proc or not self.proc.stdin or self.proc.stdin.closed: wx.Bell(); return
		self.proc.stdin.write(text + os.linesep)
		self.proc.stdin.flush()
	
	def canDo(self, id):
		if id==6278: return False
		else: return super().canDo(id)
	
	def setReadOnly(self, ro): return