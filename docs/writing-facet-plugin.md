# Writing facet plugin
Beyond file edition, you certainly want to be able to launch tasks that are global to the project you are working in.
For example, compile, build and run your project, update dependencies, etc.

Rather than doing like most of the editors out there, first manually open a project and then working on the files, here we took another approach:
when a file is open, try to see if it is part of a project, and if yes open the project.

A project has a root path and zero, one or more facets. A facet is a group of actions you can do on a project depending on its characteristics.
For example, a project using npm has dependency manager and git as versionning tool has two facets: npm and git.
Then, for example, the npm facet could give an option to update or run the project, while the git facet will allow to pull and push from Jane without the need to use the command-line or an external git tool.

Detecting if a file is part of a project and what facets it is composed of is most often done by looking at other files in the directory and all parent directories, stopping when a particular file has been detected and so establishing the project facets and root directory.
For example, finding a file pom.xml is certainly the sign that there is a Java project using Maven. Then we can initialize a maven facet, read the file and propose Maven specific actions in a menu, e.g. compile.
By default, when a project is found, parent directories are still searched, finally taking the outer most project found as active project. This is useful because a big project may be split into subprojects.

# Writing a facet factory plugin
To write a project factory plugin, import FacetFactory and use the FacetFactory annotation:

```python
from FacetFactory import FacetFactory

@FacetFactory
def mavenFacetFactory(path):
	...
```

A pathlib.Path object is passed to your factory function. It always represent a directory, the project root directory to be checked.

- If you recognize a facet in the root directory passed, you can return a facet object. You should extend the Facet class.
- IF you don't recognize any project at the path specified, return None. The next facet factory will be called.
