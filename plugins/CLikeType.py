import re
from TextType import TextType, DefaultType
import re


@TextType('c', 'cc', 'cpp', 'cxx', 'h', 'hh', 'hpp', 'hxx', 'tpp', 'java', 'php', 'pl', 'js', 'cs', 'css', 'less', 'sass', 'scss')
class CLikeType(DefaultType):
	def __init__(self):
		self.direction=0
		self.level=0
	def isBlankLine(self, line, reg=re.compile(r'^[\s{}]*$')): return reg.match(line)
	def countOpens (self, line):
		return line.count('{')
	def countCloses(self, line):
		return line.count('}')
	def onEnter(self, line):
		return self.countOpens(line) - self.countCloses(line)
	def getLevel(self, line):
		opens, closes = self.countOpens(line), self.countCloses(line)
		level = self.level
		self.level += self.direction * (opens-closes)
		return min(level, self.level)
	def getLevelCalc(self, direction):
		self.direction=direction
		self.level=0
		return self.getLevel
