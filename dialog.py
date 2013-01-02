
# xbmc
import xbmcgui

# application
from utilities import *
from app_apiclient import AppApiClient
from cache import StvList
from addonutilities import show_video_dialog_byId

ACTIONS_CLICK = [7, 100]
LIST_ITEM_CONTROL_ID = 500

__addon__  = get_current_addon()
__addonpath__	= __addon__.getAddonInfo('path')

__apiclient__ = AppApiClient.getDefaultClient()
__stvList__ = StvList.getDefaultList()

itemFolderBack = {'name': '...', 'cover_medium': 'DefaultFolderBack.png', 'id': -2}

class ListDialog(xbmcgui.WindowXMLDialog):
	""" Dialog for choosing movie corrections """
	def __init__(self, *args, **kwargs):
		self.data = kwargs['data']
		self.controlId = None
		self.selectedMovie = None

	def onInit(self):
		items = []
		items.append(self._getListItem(itemFolderBack))
		for item in self.data['items']:
			li = self._getListItem(item)
			items.append(li)

		xbmc.executebuiltin("Container.SetViewMode(%d)" % LIST_ITEM_CONTROL_ID)
		try:
			self.getControl(LIST_ITEM_CONTROL_ID).addItems(items)
		except:
			log('Adding items failed')

	def _getListItem(self, item):
		#~ itemPath = 'mode=' + str(ActionCode.VideoDialogShowById) + '&amp;stv_id=' + str(item['id'])
		li = xbmcgui.ListItem(item['name'], iconImage=item['cover_medium'])
		li.setProperty('id', str(item['id']))
		#~ li.setProperty('path', str(itemPath))
		if item.get('custom_overlay'):
			li.setProperty('CustomOverlay', item['custom_overlay'])
		
		return li

	def onFocus(self, controlId):
		self.controlId = controlId

	def onAction(self, action):
		log('action: %s focused id: %s' % (str(action.getId()), str(self.controlId)))
		# if user clicked/entered an item
		if self.controlId == LIST_ITEM_CONTROL_ID and action in ACTIONS_CLICK:
			item = self.getControl(LIST_ITEM_CONTROL_ID).getSelectedItem()			
			show_video_dialog_byId(int(item.getProperty('id')), __apiclient__, __stvList__)


def open_list_dialog(tpl_data):
	print 'cwd: ' + __addonpath__
	#~ path = '/home/smid/projects/XBMC/resources/skins/Default/720p/'
	path = ''
	try:
		win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
	except ValueError, e:
		ui = ListDialog(path + "custom_MyVideoNav.xml", __addonpath__, "Default", data=tpl_data)
		ui.doModal()
		del ui
	else:
		win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		win.close()
		ui = ListDialog(path + "custom_MyVideoNav.xml", __addonpath__, "Default", data=tpl_data)
		ui.doModal()
		del ui
