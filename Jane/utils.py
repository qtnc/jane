class Object:
	def __init__(self, **kwargs):
		for k, v in kwargs.items(): setattr(self,k,v)

def identity(x): x

def first (iterable, pred = lambda x: x is not None, default=None):
	for item in iterable:
		if pred(item): return item
	return default

def firstTruthy (iterable, default=None):
	return first(iterable, identity, default)

def iterable(o):
	try: iter(o)
	except TypeError: return False
	return True

def flattened(arg):
	for i in arg:
		if iterable(i): yield from flattened(i)
		else: yield i

def flatten (seq):
	return type(seq)(flattened(seq))

