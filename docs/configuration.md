# Configuration directives

## Section accelerators
Each key/value pair in this section defines a keyboard shortcut to bind to an action. The name of the action is the key, and the shortcut is the value.
For example, `saveDocument=Ctrl+S` bind the action `saveDocument`to the shortcut `Ctrl+S`.

## Section text
This section contains directives applicables for text documents in general.

Key | Possible values | Description
-----|--------------|---------------
autowrap |  true or false | Either or not to use automatic line wrapping when opening or creating a new document
encoding | One of the supported encodings, e.g. utf-8, cp1252 | The default encoding of a new document when nothing is defined in a .editorconfig file
indentation | 0-8 inclusive | the default indentation style and size when nothing is defined in a .editorconfig file. 0 means tabs, any other integer means that number of spaces
lineEnding | crlf, lf or cr | The default kind of line ending for new documents when nothing is defined in a .editorconfig file
onBackspaceInIndent | unindent or clear | At the beginning of a line with indentation, indicates what happens when pressing **backspace**: unindent=remove a level of indentation, clear=clear up to the beginning of the line and go back to the end of the previous line, by symetry with what happens when pressing **delete** at the end of a line

## Section extensions
Each key in this section indicates an extension module to be loaded. The key may not have a value.

You can specify a key `path`that will contain a list of paths to be appended to sys.path for module loading. Multiple paths can be separated by `os.pathsep`, i.e. `;`on windows and `:`on linux.

