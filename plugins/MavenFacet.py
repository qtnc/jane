import wx, os, re, pickle, functools, zipfile, subprocess, threading
import utils, MenuManager
from pathlib import Path
from Facet import Facet
from FacetFactory import FacetFactory
from TextType import TextType
from TextDocument import TextDocument

@FacetFactory
def mavenFacetFactory(path):
	return MavenFacet() if Path(path, 'pom.xml').exists() else None

class MavenFacet(Facet):
	def getSpecificMenus(self):
		return [('Maven', MVN_MENU)]
	
	def open(self, project):
		self.root = project.root
		self.classes = {}
		self.testClasses = {}
		self.loadClassCache()
		if not self.classes: threading.Thread(target=self.updateImportClasses).start()
		threading.Thread(target=self.updateProjectClasses).start()
	
	def loadClassCache(self):
		try:
			with open(Path(self.root, MVN_LOCAL_CACHE_FILENAME), 'rb') as file: self.classes, self.testClasses  = pickle.load(file)
		except OSError: pass
	
	def saveClassCache(self):
		try:
			with open(Path(self.root, MVN_LOCAL_CACHE_FILENAME), 'wb') as file: pickle.dump([self.classes, self.testClasses], file)
		except OSError: pass
	
	def findAutoImport(self, name, test=False, hints=set()):
		fullnames = self.classes[name] if name in self.classes else (self.testClasses[name] if test and name in self.testClasses else set())
		candidates = (fullnames & hints) or fullnames
		if len(candidates)==1: return utils.first(candidates)
		elif len(candidates)==0: return None
		else: return repr(candidates)
	
	def updateProjectClasses(self):
		for p in self.root.glob('**/src/main/java/**/*.java'):
			s=str(p); fullname=s[s.rfind('java'+os.path.sep)+5:-5].replace(os.path.sep, '.'); name = fullname[1+fullname.rfind('.'):]
			self.referenceClass(name, fullname, None, 'compile')
		for p in self.root.glob('**/src/test/java/**/*.java'):
			s=str(p); fullname=s[s.rfind('java'+os.path.sep)+5:-5].replace(os.path.sep, '.'); name = fullname[1+fullname.rfind('.'):]
			self.referenceClass(name, fullname, None, 'test')
	
	def updateImportClasses(self):
		print('Proceeding to import classes')
		reg = re.compile(r'^\[INFO\]\s*(?P<groupId>\S+):(?P<artifactId>\S+):(?P<packaging>\S+):(?P<version>\S+):(?P<scope>\S+)')
		self.referenceJar(Path(JAVA_PATH, 'jre', 'lib', 'rt.jar'))
		for line in subprocess.run('{0} {1}' .format(MVN_PATH, 'dependency:list'), encoding='utf-8', errors='replace', cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) .stdout .splitlines():
			m = reg.match(line)
			if not m: continue
			jarFile = Path(MVN_REPO_PATH, m['groupId'].replace('.', os.path.sep), m['artifactId'], m['version'], m['artifactId']+'-'+m['version']+'.'+m['packaging'])
			if not jarFile.exists(): continue
			if m['scope'] not in ('compile', 'test'): continue
			self.referenceJar(jarFile, m['scope'])
		self.saveClassCache()
	
	def referenceJar(self, jarFile, scope='compile'):
		try:
			with zipfile.ZipFile(jarFile, 'r') as zip:
				for name in zip.namelist():
					if not name.endswith('.class') or '$' in name: continue
					p = Path(name); name=p.stem; fullname=str(p).replace(os.path.sep, '.')[:-6]
					self.referenceClass(name, fullname, jarFile, scope)
		except OSError as e: print(e)
	
	def referenceClass(self, name, fullname, jarFile, scope):
		if packageOf(fullname)=='java.lang' or name in ('String', 'Integer', 'Double', 'Boolean', 'Object'): return
		cls = self.testClasses if scope=='test' else self.classes
		if name in cls: cls[name].add(fullname)
		else: cls[name] = {fullname}


def mvnGoalAction(goal, e=None):
	cmd = '"' + str(MVN_PATH) + '" ' + goal
	proj = win.document.project
	win.newDocument(type='_subprocess', name='mvn '+goal, cmd=cmd, cwd=proj.root, project=proj)

def mvnGoalActionFunc(goal):
	f = functools.partial(mvnGoalAction, goal)
	f.__name__ = 'mvn '+goal
	return f

def packageOf(name):
	return name[:name.rfind('.')]

def mvnAutoImport(self):
	doc = win.document
	mvn = doc.project.getFacet(MavenFacet)
	editor = doc.editor
	text = editor.GetValue()
	isTest = doc.file and doc.file.stem.endswith('Test')
	ipos = 1+text.find('\n')
	regType = re.compile(r'^[A-Z_]+$')
	regImport = re.compile(r'^import (?!static)\s*([^;*\n]+);\s*\n', re.M)
	regPackage = re.compile(r'^package (.*?);', re.M)
	package = regPackage.search(text)
	package = package[1] if package else None
	hints = set(regImport.findall(text))
	classes = {c for c in re.findall(r'\b[A-Z][A-Za-z0-9_]*\b', text)}
	imports = ('import {0};'.format(x) for x in sorted(i for i in (mvn.findAutoImport(c, isTest, hints) for c in classes) if i and packageOf(i)!=package))
	text = regImport.sub('', text)
	text = text[:ipos] + '\n' + '\n'.join(imports) + '\n' + text[ipos:]
	editor.SetValue(text)


app.loadTranslation('MavenFacet')
app.loadConfig('MavenFacet')

MVN_PATH = Path(app.config.get('maven', 'mavenPath'), 'bin', 'mvn.cmd' if os.name=='nt' else 'mvn')
MVN_REPO_PATH = Path(app.config.get('maven', 'repositoryPath'))
JAVA_PATH = Path(app.config.get('maven', 'javaPath'))
ONSAVE = app.config.getboolean('maven', 'autoImportOnSave', fallback=False)
MVN_GOAL_ACTIONS = tuple(x.strip() for x  in app.config.get('maven', 'goals', fallback='clean, compile, test, package, install, clean package, clean install') .split(','))
MVN_LOCAL_CACHE_FILENAME = '.mvn-jane-local-cache'

MVN_MENU = (
	*((mvnGoalActionFunc(goal), wx.ID_ANY) for goal in MVN_GOAL_ACTIONS),
	(mvnAutoImport, wx.ID_ANY)
)


