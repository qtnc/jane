# The smart paste feature
Most notably when editing python code, errors occurs because the indentation don't match between what you are pasting and where you are pasting code.
The smart paste feature tries to solve this problem.
The base principle is to adapt the indentation of the pasted code to where it is pasted.

Here's the base recipe of what happens when text is pasted into the text editor:

1. Look at the text that is going to be pasted, and remove from it all common indentation, i.e. all spaces or tabs that are found at the beginning of each line
2. Look at the indentation level where the cursor is, and indent all lines of the text being pasted by that level of indentation
3. Insert the modified text
