from TextDocument import TextDocument
from collections import OrderedDict
import utils

types = OrderedDict(
	text = TextDocument
)

factories = []

default = 'text'

def setDefault (t):
	if t in types: default=t

def newDocument (type, name, *args, **kwargs):
	return types[type or default](file=None, name=name, *args, **kwargs)

def openDocument (file=None, name=None, data=None, *args, **kwargs):
	return utils.first(f(file=file, name=name or (file.name if file else None), *args, **kwargs) for f in factories) or types[default](file=file, name=name or (file.name if file else None), *args, **kwargs)

# Intended to be used as annotation by plugins
def DocumentFactory (factory):
	factories.append(factory)
	if hasattr(factory.__name__) and factory.__name__.endswith('Document'): types[factory.__name__[:-8].lower()] = factory
	return factory
