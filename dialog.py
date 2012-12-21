
# xbmc
import xbmcgui

# application
from utilities import *


__addon__  = get_current_addon()
__cwd__	= __addon__.getAddonInfo('path')


class ListDialog(xbmcgui.WindowXMLDialog):
	""" Dialog for choosing movie corrections """
	def __init__(self, *args, **kwargs):
		self.data = kwargs['data']
		self.controlId = None
		self.selectedMovie = None

	def onInit(self):
		items = []
		for item in self.data['items']:
			li = xbmcgui.ListItem(item['name'], iconImage=item['cover_medium'])
			li.setProperty('id', str(item['id']))
			li.setProperty('CustomOverlay', item['custom_overlay'])
			items.append(li)

		xbmc.executebuiltin("Container.SetViewMode(500)")
		try:
			self.getControl(500).addItems(items)
		except:
			log('Adding items failed')
			

	def onFocus(self, controlId):
		self.controlId = controlId

	def onAction(self, action):
		log('action: %s focused id: %s' % (str(action.getId()), str(self.controlId)))


def open_list_dialog(tpl_data):
	print 'cwd: ' + __cwd__
	#~ path = '/home/smid/projects/XBMC/resources/skins/Default/720p/'
	path = ''
	try:
		win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
	except ValueError, e:
		ui = ListDialog(path + "custom_MyVideoNav.xml", __cwd__, "Default", data=tpl_data)
		ui.doModal()
		del ui
	else:
		win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		win.close()
		ui = ListDialog(path + "custom_MyVideoNav.xml", __cwd__, "Default", data=tpl_data)
		ui.doModal()
		del ui
