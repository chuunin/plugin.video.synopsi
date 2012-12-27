
# xbmc
import xbmcgui

# application
from utilities import *


ACTIONS_CLICK = [7, 100]
LIST_ITEM_CONTROL_ID = 500

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
			itemPath = 'mode=' + str(ActionCode.VideoDialogShowById) + '&amp;stv_id=' + str(item['id'])
			li = xbmcgui.ListItem(item['name'], iconImage=item['cover_medium'])
			li.setProperty('id', str(item['id']))
			li.setProperty('path', str(itemPath))
			li.setProperty('CustomOverlay', item['custom_overlay'])
			items.append(li)

		xbmc.executebuiltin("Container.SetViewMode(%d)" % LIST_ITEM_CONTROL_ID)
		try:
			self.getControl(LIST_ITEM_CONTROL_ID).addItems(items)
		except:
			log('Adding items failed')


	def onFocus(self, controlId):
		self.controlId = controlId

	def onAction(self, action):
		log('action: %s focused id: %s' % (str(action.getId()), str(self.controlId)))
		# if user clicked/entered an item
		if self.controlId == LIST_ITEM_CONTROL_ID and action in ACTIONS_CLICK:
			item = self.getControl(LIST_ITEM_CONTROL_ID).getSelectedItem()
			#~ xbmc.executebuiltin('RunScript(plugin.video.synopsi, 0, %s)' % item.getProperty('path'))
			log('clicked params:' + str(item.getProperty('path')))
			xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi/addon.py?%s)' % item.getProperty('path'))


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
