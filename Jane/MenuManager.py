import wx

def getkey (obj, key, defaultValue=None):
	try: return getattr(obj,key)
	except (AttributeError, TypeError):
		try: return obj[key]
		except (KeyError, TypeError): return defaultValue

def addItem (menu, key, id, kind=wx.ITEM_NORMAL, checked=False, table=None, handlerobj=None, binder=None):
	accelerators = app.config['accelerators'] if app.config.has_section('accelerators') else {}
	if id==wx.ID_NONE: return
	elif id==wx.ID_SEPARATOR: menu.AppendSeparator(); return
	if binder is None: binder=win
	if handlerobj is None: handlerobj=binder
	handler = getkey(handlerobj, key)
	if not handler and callable(key): handler=key
	if not handler and callable(handlerobj) and not isinstance(handlerobj,type): handler = handlerobj
	if not isinstance(key,str): key = key.__name__
	label = translate(key)
	help = translate(key+'Help')
	shortcut = accelerators.get(key, None)
	item = menu.Append(id, label, help, kind=kind)
	if kind!=wx.ITEM_NORMAL and checked: item.Check(checked)
	if handler and binder: binder.Bind(wx.EVT_MENU, handler, id=item.GetId())
	if shortcut and table is not None:
		entry = wx.AcceleratorEntry(cmd=item.GetId(), item=item)
		if entry.FromString(shortcut):
			item.SetItemLabel(item.GetItemLabel() + '\t' + entry.ToString())
			table.append(entry)
	return item

def addItems (menu, items, table=None, handlerobj=None, binder=None):
	if isinstance(items,dict): items=items.items()
	return [addItem(menu, *item, table=table, handlerobj=handlerobj, binder=binder) for item in items]
	