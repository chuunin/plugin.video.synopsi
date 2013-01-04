
# xbmc
import xbmcgui

# application
from utilities import *
from addonutilities import show_video_dialog_byId, OverlayCode, overlay_image

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
			listControl = self.getControl(LIST_ITEM_CONTROL_ID)
			listControl.addItems(items)
			self.setFocus(listControl)
		except:
			log('Adding items failed')

	def _getListItem(self, item):
		#~ itemPath = 'mode=' + str(ActionCode.VideoDialogShowById) + '&amp;stv_id=' + str(item['id'])
		li = xbmcgui.ListItem(item['name'], iconImage=item['cover_medium'])
		li.setProperty('id', str(item['id']))
		#~ li.setProperty('path', str(itemPath))
			
		# prefer already set custom_overlay, if N/A set custom overlay
		if item.get('custom_overlay'):
			li.setProperty('CustomOverlay', item['custom_overlay'])
		else:
			oc = self._getItemOverlayCode(item)
			li.setProperty('CustomOverlay', overlay_image[oc])
			
		return li

	def _getItemOverlayCode(self, item):
		overlayCode = OverlayCode.Empty
		if item.get('file'):
			overlayCode += OverlayCode.OnYourDisk
		if item.get('watched'):
			overlayCode += OverlayCode.AlreadyWatched
			
		return overlayCode

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
		xbmc.executebuiltin("Container.SetViewMode(503)")

def open_list_dialog(tpl_data, close=False):
	log('open_list_dialog cwd: ' + __addonpath__)
	#~ path = '/home/smid/projects/XBMC/resources/skins/Default/720p/'
	
	path = ''
	try:
		win = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
	except ValueError, e:
		log('V1')
		ui = ListDialog(path + "MyVideoNav.xml", __addonpath__, "Default", data=tpl_data)
		ui.doModal()
		del ui
	else:
		log('V2')
		win = xbmcgui.WindowDialog(xbmcgui.getCurrentWindowDialogId())
		if close:
			win.close()
		ui = ListDialog(path + "MyVideoNav.xml", __addonpath__, "Default", data=tpl_data)
		ui.doModal()
		del ui

def show_movie_list(item_list, dirhandle):
	errorMsg = None
	try:
		if not item_list:
			raise ListEmptyException

		open_list_dialog({ 'items': item_list })

	except AuthenticationError:
		errorMsg = True
	finally:
		pass
		#~ log('A1')
		#~ xbmcplugin.endOfDirectory(dirhandle)
		#~ xbmc.executebuiltin("Container.SetViewMode(500)")

	if errorMsg:
		if dialog_check_login_correct():
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi, replace)')

	# xbmc.executebuiltin('Container.Update(plugin://plugin.video.synopsi?url=url&mode=999)')



