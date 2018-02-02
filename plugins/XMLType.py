import re
from TextType import TextType, DefaultType
from CLikeType import CLikeType

@TextType('xml', 'htm', 'html', 'xhtml', 'hta', 'xsd', 'xsl', 'svg')
class XMLType(CLikeType):
	def isBlankLine(self, line, reg=re.compile(r'^(?:\s*</[-a-zA-Z_0-9:]+>)*\s*$')): return reg.match(line)
	def countOpens(self, line, reg=re.compile(r'<(?!/).*?(?<!/)>')):	
		count = len(reg.findall(line))
		return count
	def countCloses(self, line, reg=re.compile(r'</.*?>')):	
		count = len(reg.findall(line))
		return count
