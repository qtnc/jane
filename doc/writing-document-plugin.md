# Writing document plugin
Maybe in the future, we might not only want to edit text or source code files.
Perhaps you want to implement syntactic auto-formatting yourself and totally supercede the default text editor component ?
Or, for a particular file type, you want something else than a simple text area ?
You know what ? WE can !

Among other possibilities here, we can imagine:

- Hexadecimal editor for binary files
- Edition in a tree view for XML and HTML files

# Writing a document factory plugin
To write a document factory plugin, import DocumentFactory and use the DocumentFactory annotation:

```python
from DocumentFactory import DocumentFactory

@DocumentFactory
def binaryDocumentFactory(file=None, name=None, data=None, *args, **kwargs):
	...
```

A serie of arguments are passed to your factory function. All of them may be None. Most popular are:

- file: a pathlib.Path object representing the file to open
- name: the name of the tab; most often the file name without path, or things like "untitled 1"
- data: the data read from the file, as bytes; in general given only when the file doesn't exist or is unknown, as when reading from clipboard, standard input or network for example

- IF you can create a document with the arguments passed, return a Document object. You must extend the Document class, and, generally, pass all arguments to your constructor, and then to the constructor of Document in your __init__ method.
- IF you don't recognize any document with the parameters given, return None. The next document factory will be called, and finally the default one.
