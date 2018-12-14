# Jane: just another editor
Jane is a text editor especially made to be accessible to screen readers.
It is made in python 3 and is using wxPython for its GUI interface.

Just another editor, why ? because it is just another trial after my two previous more or less failed attempts: [6pad](http://github.com/qtnc/6pad) in 2012-2013 and [6pad++](http://github.com/qtnc/6pad2) in 2015-2016.
They worked, well, but C and then C++ were still difficult to master, and I used the Win32 API for GUI, what was also source of strange bugs that have never been solved.
For this third attempt, I decided to start again from the beginning, doing everything in Python and by using the WXPython library for GUI.
I hope with this choice that this new editor will be more maintainable, have less unexplained bugs, and  that python will encourage more people to contribute than C or C++. Additionally WXPython is portable, which is also good because more and more sceen reader users switch to Mac or Linux.

# Features
Main distinctive features of Jane includes :

* Edit multiple files in a tabbed interface
* Read and write files in most popular character encodings as well as 80 less popular ones
* Search and replace using regular expressions
* Open files at lightning speed, even for big files of a few dozends megabytes.
* Prevent opening a file twice in different tabs, and automatically refereshing file's contents when modified in another external program.
* Use pipes to quickly read results of DOS command, or simply send them input without making temporary files
* Use the powerful jump to feature and extended navigation shortcuts to quickly move between and within files in your development projects

# Download (for users)
You can download an early binary release for windows 7, 8 and 10, 32 bits at the link below.
If you have a Mac, sorry, but I don't have one myself, so you will have to build executables for your system yourself.

Note that it's still an extremely early alpha release. Some features are incomplete, and there are probably still a lot of bugs or inconsist behaviors. I wouldn't advise you to use it as your main text editor yet.
Now that you are warned, you can [download Jane version 0.0 for Windows 7, 8 and 10 32-bit. Zip file of about 25 MB once uncompressed](http://vrac.quentinc.net/Jane-0.0.zip)

Feel free to post your comments or bug reports.

# Installation (for developers and contributors)
Jane requires [python](http://www.python.org/) version 3.6.4 at least, as well as the following third-partie modules. You can install them with pip:

- [wxPython](http://wxpython.org/)
- [editorconfig](https://github.com/editorconfig/editorconfig-core-py)

You may also optionaly install cx_Freeze, if you want to build an executable, distribution package or installer. A script to do so is included.

# Documentation
You can find documentation in the docs directory. Currently these documents are available:

- [Menu commands](docs/menus.md)
- [Keyboard navigation](docs/navigation.md)
- [Configuration](docs/configuration.md)
- [.editorconfig support](docs/doteditorconfig.md)
- [The jump to feature](docs/jump-to-feature.md)
- [The smart paste feature](docs/smart-paste-feature.md)
- [Writing document plugin](docs/writing-document-plugin.md)
- [Writing facet plugin](docs/writing-facet-plugin.md)
- [Writing text type plugin](docs/writing-text-type-plugin.md)

# Extension plugins
Three kinds of plugins can be written. They allow to handle more types of documents, and more kinds of project facets.
Plugins are just python modules that are imported when Jane starts. IN order to work, they must be placed in a directory from where they can be imported.

## Available plugins
Plugin name | Type | Description
------------|-----|-----------------------------
[Astyle](docs/plugin-astyle.md)  | Text type | Format Java, C/C++ and C# source code using [Artistic style](http://astyle.sourceforge.net/)
CLikeType | Text type | Provite Alt+Arrow keys navigation in bracket-based languages such as C, C++, Java, C#, PHP, CSS/less/sass/scss
MarkdownType | Text type | activate read-only mode  and use familiar quick key navigation to navigate in markdown documents, such as H to go to next heading. H, Q, L, T, 1, 2, 3, 4, 5 are supported.
PythonType | Text type | Provide Alt+Arrow keys navigation for languages based on indentation such as python
XMLType | Text type | Provide Alt+Arrow keys navigation for XML-based languages. Requires CLikeType


## Third-partie plugins
The following plugins are third-partie plugins that the developers of Jane find worth it.
In case of problems, please file an issue to their authors rather then here.

Currently none



# Story
Since a long time, I have been frustrated by default windows' notepad because of its lack of functionalities for developers.
There are of course dedicated text editors especially made for developers, but I wheither find them too heavy, or not as accessible as I would like with a screen reader.

For example, notepad2 and notepad++ are very lightweight, but only partially accessible. Screen readers don't always behave as they should, or don't always read what they need to when necessary.
IN the opposite side, complete integrated developement editors like [eclipse](http://eclipse.org/) are known to be not so badly accessible, but they are most of the time too heavy, not so easy to use, take time to start up, and aren't that suited to have a quick look at small files and other notes.
They also do a lot of things under the hoo that aren't always desired and these things aren't easy to configure.

There effectively already exist a text editor made for screen reader users, it is called [EdSharp](http://empowermentzone.com/EdSharp.htm).
However, I find its interface not as easy as it is said; menus are especially full of rarely used features, are quite randomly mixed up, and it lacks an obvious possibility of customizing the whole thing in an easy way. And, of course, I don't program in C#.

# Contributing
If you have great ideas, found a bug or want to improve documentation, feel free to post issues and send pull requests. You can of course also write me an e-mail directly.
Don't hesitate to also share extensions you made.

Have fun !

# License
Jane is distributed as a free software with the [GNU GPL version 3 license](license.txt).
For more information, read license.txt.

