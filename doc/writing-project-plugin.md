# Writing project plugin
Beyond file edition, you certainly want to be able to launch tasks that are global to the project you are working in.
For example, compile, build and run your project, update dependencies, etc.

Rather than doing like most of the editors out there, first manually open a project and then working on the files, here we took another approach:
when a file is open, try to see if it is part of a project, and if yes open the project.

Detecting if a file is part of a project and what kind of project is most often done by looking at other files in the directory and all parent directories, stopping when a particular file has been detecte and so establishing the project type and root directory.
For example, finding a file pom.xml is certainly the sign that there is a Java project using Maven. Then we can read the file and propose Maven specific actions in a Project menu, e.g. compile.

By default, when a project is found, parent directories are still searched, finally taking the outer most project found as active project. This is useful for example with Maven projects, where a big project is often split into submodules.

# Writing a project factory plugin
To write a project factory plugin, import ProjectFactory and use the ProjectFactory annotation:

```python
from ProjectFactory import ProjectFactory

@ProjectFactory
def mavenProjectFactory(path):
	...
```

A pathlib.Path object is passed to your factory function. It always represent a directory, the project root directory to be checked.

- If you recognize a project in the root directory passed, you can return a Project object. You should extend the Project class. You can also return True or False as second return value, True to stop searching in parent directories immediately.
- IF you don't recognize any project at the path specified, return None. The next project factory will be called.
