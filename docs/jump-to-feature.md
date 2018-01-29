# The jump to feature
Use Ctrl+J to quickly jump somewhere, in the same or another file.
Definitely a powerful command !

# Supported syntaxes in jump to feature
## For text files
Syntax | Effect
---------|------------
12 | Go to line 12 (start counting at 1)
12,3 | Go to line 12, character 3 (start counting characters at 1 from the beginning of the line)
12:3 | Idem, alternative syntax
[12,3] | Idem, yet another syntax
12-34 | Select from beginning of line 12 to end of line 34
12,3-45,6 | Select from line 12, character 3 to line 45, character 6
+8 | Go down 8 lines
-8 | Go up 8 lines

## For projects
This implies that a project must be open / that the file is within a project

Syntax | Effect
---------|------------
readme.md | Go to file readme.md; the file is opened if necessary; if the file is already open, then its tab is focused; the file is searched in the project root directory and all subdirectories.
hello.py:4 | Go to line 4 of hello.py; note that you can combine a file name with all combinations presented above, i.e. hello.py:4,7, hello.py[4,7] and hello.py:4-7 work
hello | Go to a file named hello having the same suffix as the current file, p.ex. hello.py if another .py is already open.
hel | Go to a file with a name starting with hel and having the same suffix as the current file; in our example, hello.ply would be found, as long as there isn't any ambiguity; if there is an ambiguity, a menu asking for the file to open is shown.
tfd | If no file starting with tfd is found, then a file starting with T, containing an F and a D (in that order) will be searched. e.g. TextFindDialog.py
TFo | When typing only TF in the project of this editor, we could find TextFormat.py and TextFlavor.py. To remove ambiguity, we look for a file starting with T and containing Fo.

# Idead of additional syntaxes
These syntaxes are only ideas open for discussion; they aren't implemented yet. Give your opinion !

- Search for the text "ab" in the current file using `#abc` or `@abc` or `~abc`; of course, more powerful when combining with a file name, e.g. `test.py@yes` would jump to the first occurence of "yes" in test.py
- Search for "abc" as regex using `/abc` or `:/abc` (to disambiguate with file paths), + regex options with `/abc/i`
- Search for "abc" only if it appears at beginning of line with `^abc`
- Search/replace with regex: `s/search/replacement/options`
- Filter by doing something like grep: `f/regex/options` or `^regex` or `~regex`.
- Go to symbol, e.g. function declaration: `#abc` or `@abc` or `%abc` or `::abc`, + maybe different kinds of symbols according to the prefix character used. Difficulty: must be dependent of the programming language of the file currently open
- Insert a character: `&xE9` or `&233`
- run "dir" command and insert the result at cursor position or in a new tab: `$dir` or `>dir`
- Compute `1+2*3` and insert the result at cursor position: `=1+2*3`, + why not a full monoline python expression
- Replace the text field with a combo box and keep the last  10, 20 or 50 jumps performed ?