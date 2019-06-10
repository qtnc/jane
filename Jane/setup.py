import os
from os import path
from glob import glob
from cx_Freeze import setup, Executable

name = 'Jane'
version = '0.0'
base = 'Win32GUI' if os.name=='nt' else None

osext = { 'nt': '.exe', 'darwin': '.app'}

buildOptions = dict(
	optimize=2,
	includes = ['editorconfig', 'natsort'],
	zip_include_packages='*',
	zip_exclude_packages=(),
	include_files = [(file, path.basename(file)) for file in glob('../' + name + '*.*')] + [(file, path.basename(file)) for file in glob('../plugins/**')],
	zip_includes = [],
	include_msvcr = True
)

executable = Executable(
	script='__main__.py',
	base=base,
	targetName=name + osext.get(os.name, ''),
	shortcutName=name,
	copyright = 'Copyright \u00A9 2018, Quentin Cosendey (http://quentinc.net/)'
)

setup(
	name=name,
	version=version,
	executables=[executable],
	options={'build_exe': buildOptions}
)