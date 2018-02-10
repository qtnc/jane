import wx, utils

def getkey (obj, key, defaultValue=None):
	try: return getattr(obj,key)
	except (AttributeError, TypeError):
		try: return obj[key]
		except (KeyError, TypeError): return defaultValue

def addItem (menu, key, id=wx.ID_ANY, kind=wx.ITEM_NORMAL, checked=False, index=None, table=None, handlerobj=None, binder=None):
	accelerators = app.config['accelerators'] if app.config.has_section('accelerators') else {}
	if id==wx.ID_NONE: return
	elif id==wx.ID_SEPARATOR:
		if index is None: return menu.AppendSeparator()
		else: return menu.InsertSeparator(index)
	elif utils.iterable(id):
		return addSubMenu(menu, key, id, index, table, handlerobj, binder)
	if binder is None: binder=win
	if handlerobj is None: handlerobj=binder
	handler = getkey(handlerobj, key)
	if not handler and callable(key): handler=key
	if not handler and callable(handlerobj) and not isinstance(handlerobj,type): handler = handlerobj
	trArgs = None
	if isinstance(key,tuple): key, *trArgs = key
	if not isinstance(key,str): key = key.__name__
	label = translate(key)
	if trArgs: label = label.format(*trArgs)
	help = translate(key+'Help', None)
	if help and trArgs: help = help.format(*trArgs)
	shortcut = accelerators.get(key, None)
	if index is None: item = menu.Append(id, label, help, kind)
	else: item = menu.Insert(index, id, label, help, kind)
	if kind!=wx.ITEM_NORMAL and checked: item.Check(checked)
	if handler and binder: binder.Bind(wx.EVT_MENU, handler, id=item.GetId())
	if shortcut and table is not None:
		entry = wx.AcceleratorEntry(cmd=item.GetId(), item=item)
		if entry.FromString(shortcut):
			item.SetItemLabel(item.GetItemLabel() + '\t' + entry.ToString())
			table.append(entry)
	return item

def addItems (menu, items, index=None, table=None, handlerobj=None, binder=None):
	if isinstance(items,dict): items=items.items()
	if index is None: return [addItem(menu, *item, table=table, handlerobj=handlerobj, binder=binder) for item in items]
	else: return [addItem(menu, *item, index=i, table=table, handlerobj=handlerobj, binder=binder) for i, item in enumerate(items, index)]

def addSubMenu(menu, key, items, index=None, table=None, handlerobj=None, binder=None):
	submenu = wx.Menu()
	addItems(submenu, items, None, table, handlerobj, binder)
	if index is None: menu.AppendSubMenu(submenu, translate(key), translate(key+'Help', None))
	else: menu.Insert(index, wx.ID_ANY, translate(key), submenu, translate(key+'Help', None))
	return submenu

def addMenu (menubar, key, items, index=None, table=None, handlerobj=None, binder=None):
	menu = wx.Menu()
	addItems(menu, items, None, table, handlerobj, binder)
	key = translate(key)
	if index is None: menubar.Append(menu, key)
	else: menubar.Insert(index, menu, key)

def addMenus (menubar, items, index=None, table=None, handlerobj=None, binder=None):
	if index is None: return [addMenu(menubar, *item,  table=table, handlerobj=handlerobj, binder=binder) for item in items]
	else: return [addMenu(menubar, *item,  index=i, table=table, handlerobj=handlerobj, binder=binder) for i, item in enumerate(items, index)]

def deleteItems (menu, start=0, end=None):
	start, end, step = slice(start, end) .indices(menu.GetMenuItemCount())
	for i in range(end -1, start -1, -1): menu.DestroyItem(menu.FindItemByPosition(i))

def deleteMenus (menubar, start=0, end=None):
	start, end, step = slice(start, end) .indices(menubar.GetMenuCount())
	for i in range(end -1, start -1, -1): menubar .Remove(i) .Destroy()

def replaceItems (menu, start=0, end=None, items=(), table=None, handlerobj=None, binder=None):
	deleteItems(menu, start, end)
	return addItems(menu, items, start, table, handlerobj, binder)

def replaceMenus (menubar, start=0, end=None, items=(), table=None, handlerobj=None, binder=None):
	deleteMenus(menubar, start, end)
	return addMenus(menubar, items, start, table, handlerobj, binder)

def spliceMenus (menubar, start=0, count=0, items=(), table=None, handlerobj=None, binder=None):
	return replaceMenus(menubar, start, start+count, items, table, handlerobj, binder)
