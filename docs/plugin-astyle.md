# Astyle plugin
The astyle plugin allow to format C, C++, Java and C# source code using [Artistic style](http://astyle.sourceforge.net/).

The following options can be set in configuration ini file, in a section `astyle`:

Option | Value type | Description
-----|-----|-----
autoformatOnLoad | true or false | When true, your source code is automatically formatted on load; default false
autoformatOnSave | true or false | When true, your source code is automatically formatted on save; default false
options | string | Formatting options to pass to astyle on the command-line; see astyle documentation for the numerous options that you can pass
path | string | Full path to astyle executable. If omited, assume that astyle is available on the system path.
