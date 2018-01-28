# Writing text type plugin
A text type implements behaviors for specific types of source codes.
For exemple, suffix .py is associated with PythonType and PythonType causes indentation to be increased at next line when you press enter on a line ending with a colon.

## Which behaviors TextType can implement
todo

# Writing a TextType plugin
To write a TextType plugin, import TextType and use the TextType annotation on a class or factory function.

You can use the TextType annotation with or without parameters:

- With parameters: parameters represent one or more suffixes; when the file name ends with one of the given suffixes, your factory function is called without arguments. You must return an object. You are advised to extend DefaultType.
- Without parameters: your factory function is called with 2 arguments: file, a pathlib.Path, and text, the contents of the file; both may be None. IF you return None, the next factory is called; otherwise you must return an object. You are advised to extend DefaultType.

