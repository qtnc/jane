import re
from pathlib import Path
from os import path
import utils, FacetFactory

projects = {}

class Project:
	def __init__ (self, root, facets=None):
		self.root=root
		self.facets=facets or []
	
	def open(self):
		for facet in self.facets: facet.open(self)
	
	def getSpecificMenus(self):
		return utils.flatten(tuple(x.getSpecificMenus() for x in self.facets))
	
	def findFiles (self, fn, base=None):
		name, ext = path.splitext(fn)
		if base and not ext: pat  = '**/' + name + '*' + base.suffix
		else: pat = '**/' + fn
		result = list(self.root.glob(pat))
		if result: return result
		if fn.islower(): pat = '**/' + '*'.join(fn) + '*' + base.suffix
		else: pat = '**/' + '*'.join(re.findall(r'[A-Z][^A-Z]*', fn)) + '*' + base.suffix
		result = list(self.root.glob(pat))
		if result: return result
		return ()





def getProjectOf (file):
	global projects
	project = None
	for path, project  in projects.items():
		if path in file.parents: return project
	for path in file.parents:
		facets = list(filter(lambda f: f(path), FacetFactory.factories)) 
		if facets: p=Project(path, facets)
		else: p = Project(path) if isUntypedProject(path) else None
		if p: project=p
	if project: projects[project.root] = project; project.open()
	return project

def isUntypedProject   (path):
	files = { 'pom.xml', 'build.xml', 'package.json', '.git', '.gitignore', '.svn', '.hg', '.editorconfig', '.settings', '.project', 'requirments.txt', 'readme.txt', 'readme.md', 'readme.rst'  }
	for file in path.glob('*.*'):
		return file.name in files
