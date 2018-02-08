import os, re, zipfile, subprocess, threading
import utils
from pathlib import Path
from Facet import Facet
from FacetFactory import FacetFactory

MVN_PATH = r"C:\Java\apache-maven-3.5.0\bin\mvn.cmd"
MVN_REPO_PATH = r"C:\Users\Quentin\.m2\repository"
RT_JARS = [r"C:\Java\JDK8\jre\lib\rt.jar"]

@FacetFactory
def mavenFacetFactory(path):
	return MavenFacet() if Path(path, 'pom.xml').exists() else None

class MavenFacet(Facet):
	def open(self, project):
		self.root = project.root
		self.classes = {}
		threading.Thread(target=self.updateClasses).start()
	
	def updateClasses(self):
		for p in self.root.glob('**/src/main/java/**/*.java'):
			s=str(p); fullname=s[s.rfind('java'+os.path.sep)+5:-5].replace(os.path.sep, '.'); name = fullname[1+fullname.rfind('.'):]
			self.referenceClass(name, fullname, None, 'compile')
		for p in self.root.glob('**/src/test/java/**/*.java'):
			s=str(p); fullname=s[s.rfind('java'+os.path.sep)+5:-5].replace(os.path.sep, '.'); name = fullname[1+fullname.rfind('.'):]
			self.referenceClass(name, fullname, None, 'test')
	
	def updateClasses2(self):
		self.classes = {}
		self.testClasses = {}
		reg = re.compile(r'^\[INFO\]\s*(?P<groupId>\S+):(?P<artifactId>\S+):(?P<packaging>\S+):(?P<version>\S+):(?P<scope>\S+)')
		for jar in RT_JARS: self.referenceJar(jar)
		for line in subprocess.run('{0} {1}' .format(MVN_PATH, 'dependency:list'), encoding='utf-8', errors='replace', cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) .stdout .splitlines():
			m = reg.match(line)
			if not m: continue
			jarFile = Path(MVN_REPO_PATH, m['groupId'].replace('.', os.path.sep), m['artifactId'], m['version'], m['artifactId']+'-'+m['version']+'.'+m['packaging'])
			if not jarFile.exists(): continue
			if m['scope'] not in ('compile', 'test'): continue
			self.referenceJar(jarFile, m['scope'])
		print('Referenced {0} names for {1} classes' .format(len(self.classes), len(utils.flatten(self.classes.values(), list))))
		print('Referenced {0} names for {1} test classes' .format(len(self.testClasses), len(utils.flatten(self.testClasses.values(), list))))
	
	def referenceJar(self, jarFile, scope='compile'):
		try:
			with zipfile.ZipFile(jarFile, 'r') as zip:
				for name in zip.namelist():
					if not name.endswith('.class') or '$' in name: continue
					p = Path(name); name=p.stem; fullname=str(p).replace(os.path.sep, '.')[:-6]
					self.referenceClass(name, fullname, jarFile, scope)
		except OSError as e: print(e)
	
	def referenceClass(self, name, fullname, jarFile, scope):
		cls = self.testClasses if scope=='test' else self.classes
		if name in cls: cls[name].add(fullname)
		else: cls[name] = {fullname}