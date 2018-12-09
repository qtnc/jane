from collections.abc import MutableSet

class OrderedSet(MutableSet):
	def __init__(self,o=()): self.set=set(o); self.list=list(o)
	def __len__(self): return len(self.list)
	def __contains__(self,key): return (key in self.set)
	def __reversed__(self): return reversed(self.set)
	def __iter__(self): return self.list.__iter__()
	def discard(self,key): self.set.remove(key); self.list.remove(key)
	def pop(self): key=self.list.pop(); self.remove(key); return key
	def add(self,key): 
		if key not in self.set: self.list.append(key); self.set.add(key)
	def push(self,key): self.add(key); self.list.remove(key); self.list.insert(0,key)
	def __getitem__(self,i): return self.list[i]
	def __delitem__(self,i): key=self.list[i]; del self.list[i]; self.set.remove(key)
	def __eq__(self,o): return set(o)==self.set
	def __repr__(self): return self.list.__repr__()

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
