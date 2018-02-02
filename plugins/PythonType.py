from TextType import TextType, DefaultType

@TextType('py')
class PythonType(DefaultType):
	def onEnter(self, line):
		return 1 if line.endswith(':') else 0
