class Object:
	def __init__(self, **kwargs):
		for k, v in kwargs.items(): setattr(self,k,v)

def identity(x): x

def isnotnone(x):
	return x is not None

def first (iterable, pred=isnotnone, default=None):
	for item in iterable:
		if pred is None or pred(item): return item
	return default

def firstTruthy (iterable, default=None):
	return first(iterable, identity, default)

def last (iterable, pred=isnotnone, default=None):
	result = default
	for item in iterable:
		if pred is None or pred(item): result=item
	return result

def iterable(o):
	if isinstance(o,str): return False
	try: iter(o)
	except TypeError: return False
	return True

def flattened(arg, maxDepth=100):
	for i in arg:
		if not iterable(i) or maxDepth<=0: yield i
		else: yield from flattened(i, maxDepth -1)

def flatten (seq, factory=None, maxDepth=100):
	if factory is None: factory=type(seq)
	return factory(flattened(seq, maxDepth))

def multicall (*funcs):
	def func(*args, **kwargs): return last((f(*args, **kwargs) for f in funcs), None)
	return func
