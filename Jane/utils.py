def first (iterator, pred = lambda x: x is not None, default=None):
	for item in iterator:
		if pred(item): return item
	return default