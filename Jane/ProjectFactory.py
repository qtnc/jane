from Project import Project
import utils

factories = []
projects = {}

def getProjectOf (file):
	global projects
	project = None
	for path, project  in projects.items():
		if path in file.parents: return project
	for path in file.parents:
		r = utils.first(f(path) for f in factories) or untypedProject(path)
		if isinstance(r,tuple): p, b = r
		else: p=r; b=False
		if p: project=p
		if b: break
	if project: projects[project.root] = project; project.open()
	return project

def untypedProject   (path):
	files = { 'pom.xml', 'build.xml', 'package.json', '.git', '.gitignore', '.svn', '.hg', '.editorconfig', '.settings', '.project', 'requirments.txt', 'readme.txt', 'readme.md', 'readme.rst'  }
	for file in path.glob('*.*'):
		if file.name in files:
			return Project(path)
	return None

# Intended to be used as annotation by plugins
def ProjectFactory (factory):
	factories.append(factory)
	return factory