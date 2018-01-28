# MEnus
Here's a short description of commands you can find in the menus.
Most obvious commands won't be described beyond their name; some commands are described elsewhere because there were a lot to say about them.

# File menu

- New: create a new document in a new tab
- Open: open a document in a new tab
- Close: close the current tab
- Reload: reload the current file
- Save: save the current file
- Save as: save the current file under a new name

# Edit menu

- Undo: undo the last action, most often the last words or lines modified/inserted/deleted. Up to 50 actions can be undone.
- Redo: redo the just undone action
- Copy: copy the selection into clipboard. If there is no selection, copy the current line
- Cut: Cut the selection into the clipboard. If there is no selection, cut the current line.
- Paste: paste the contents of the clipboard at current position, using [smart paste algorithm](smart-paste-feature.md); deleting the selection first if something was selected. 
- Find: open the find dialog to search for something in the current document; most recent searches previously done in the current session are suggested. You can use regular expressions using python syntax.
- Find and replace: open the search/replace dialog to search for something and replace it with something else; most recent searches/replacements are suggested. You can use regular expressions using python syntax.
- Mark current position: mark the current position, either to come back to it later, or to mark the beginning of a selection. If there was already a position marked, it is discarded by the new one.
- Select to mark: select from the previously marked position to the current position. This most notably allow you to select a large quantity of text without the need to keep Shift pressed all the time.
- Go to mark: place the cursor at the previously marked position
- Jump to: open the jump to dialog, allowing you to jump to another part of the file or another file. See [the jump to feature](jump-to-feature.md) for more details.

# Format menu

- Encoding: allow you to select the encoding with which the file will be saved. On open, the settings of an existing .editorconfig file is taken, or a guess is attempted if no .editorconfig exists.
- Line ending: allow you to select the line-ending type with which the file will be saved. On open, the settings of an existing .editorconfig file is taken, or a guess is attempted if no .editorconfig exists.
- Indentation: allow you to select the kind of indentation to use when pressing tab or shift+tab. On open, the settings of an existing .editorconfig file is taken, or a guess is attempted if no .editorconfig exists.
- Automatic line wrap: if this option is checked, lines that are too long to fit on screen are pushed to next lines, so that there is never an horizontal scrollbar. If this option isn't checked, an horizontal scrollbar appears if there are too long lines to fit on screen.
