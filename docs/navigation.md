# Keyboard navigation
Here we describe uncommon navigation keyboard shortcuts you can use in the text editor.
Usual shortcuts, such as Ctrl+Home/End, that you can use everywhere where there is text, are of course suppported; they won't be described here.

Common navigation shortcuts supported include:

- Arrow keys
- Shift+Arrow keys (selection)
- Ctrl+Left/right (move word by word)
- Ctrl+Shift+Left/right (select word by word)
- End (go to end of line)
- Shift+Home/end (select to beginning or end  of line)
- Ctrl+Home/End (go to beginning or end of file)
- Ctrl+Shift+Home/End (select to beginning or end of file)

# Smart home
When pressing Home, the cursor goes to the first non-blank character instead of the true beginning of the line, unless it is already on the first non-blank character.
This allow you to completely ignore indentation when you need to !

# Move by paragraph: Ctrl+Up/Down
This shortcuts is quite common for Jaws users, but not always reliable in notepad and other text editors.
Here it is re-designed to always work as intended, move by paragraph.
A paragraph is a block of text separated by at least one blank line (two line breaks in a row)

Note that you can add Shift to select to the previous/next paragraph. This isn't possible with notepad, and neither with wordpad.

# Tree-like navigation: Alt+Arrow keys, Alt+Home and Alt+End
When doing programming, it is often useful to navigate by logical block. The tree-like navigation will help you doing that and also help you getting a better overview of the code you are editing.
Most programming languages are organized into blocks nested ones into the others, forming a tree structure: in a first level we have classes, in second level methods or functions, and loop, conditional or structural blocks at third level and beyond.
So, why not navigate in the code like we are used to navigate in tree views ?

Alt+Up/Down go to the previous/next line at the same tree level. 
If there are lines of deeper levels, they are all skipped. 
If the previous/next line is of higher level, you have reached a border; the cursor stay at current line.

Alt+Left goes to the parent of current line. For example if you were inside a function, you go back to the function definition.
Probably not very useful but  to keep symetry, Alt+Right goes to the next line but only if it is of a deeper level.

Alt+Home and Alt+End go to the first or last line at the same tree level.
It works as if pressing Alt+Up or Alt+Down repeatedly until a border is reached.

In general, levels are determined by their indentation; deeper level means more indentation to the right.

For languages where indentation doesn't matter and blocks are delimited by { and }, tree-like navigation is attempted using  { and } instead of indentation
The same is also attempted with XML, determining level out of `<open-tag>`, `</closing-tag>` and `<self-closing-tag/>`. Warning though, HTML5 tags that can implicitely be self-closed (e.g. `<input>`) aren't threated specially.
