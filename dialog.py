
# xbmc
import xbmcgui

# application
from utilities import *
from addonutilities import show_video_dialog_byId

ACTIONS_CLICK = [7, 100]
LIST_ITEM_CONTROL_ID = 500
GO_BACK = -2

__addon__  = get_current_addon()
__addonpath__	= __addon__.getAddonInfo('path')

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
		
		if action in CANCEL_DIALOG:
			self.close()
		# if user clicked/entered an item
		elif self.controlId == LIST_ITEM_CONTROL_ID and action in ACTIONS_CLICK:
			item = self.getControl(LIST_ITEM_CONTROL_ID).getSelectedItem()			
			stv_id = int(item.getProperty('id'))
			if stv_id == GO_BACK:
				self.close()
			else:
				show_video_dialog_byId(stv_id)

	def close(self):
		xbmc.executebuiltin("Container.SetViewMode(503)")
		xbmcgui.WindowXMLDialog.close(self)

def open_list_dialog(tpl_data, close=False):
	log('open_list_dialog cwd: ' + __addonpath__)
	#~ path = '/home/smid/projects/XBMC/resources/skins/Default/720p/'
	
	path = ''
	try:
		win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
	except ValueError, e:
		ui = ListDialog(path + "MyVideoNav.xml", __addonpath__, "Default", data=tpl_data)
		ui.doModal()
		del ui
	else:
		win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		if close:
			win.close()
		ui = ListDialog(path + "MyVideoNav.xml", __addonpath__, "Default", data=tpl_data)
		ui.doModal()
		del ui
