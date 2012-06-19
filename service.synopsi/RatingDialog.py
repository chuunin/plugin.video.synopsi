import xbmc, xbmcgui
import os
"""
class popupList(xbmcgui.WindowDialog):
	def __init__(self, title, btns=[], items=[], width=100):
		w = int(self.getWidth()*width)
		pad = int(self.getHeight()/100)
		hCnt = 30
		yo = 30
		self.selected = [-1, -1]
		h = self.getHeight()-30*pad
		self.btns = btns
		mediaDir = os.path.join(os.getcwd(),'resources','skins','DefaultSkin','media')
		rw = self.getWidth()
		rh = self.getHeight()
		x = rw/2 - w/2
		y = rh/2 -h/2
		
		# Background
		#self.imgBg = xbmcgui.ControlImage(5+x,5+y,w,h, os.path.join(mediaDir,'popup-bg-shadow.png'))
		#self.addControl(self.imgBg)
		
		#Image load
		#self.imgBg = xbmcgui.ControlImage(0+x-30,0+y-30,w+60,h+60, os.path.join(mediaDir,'gs-bg-menu.png'))
		#self.addControl(self.imgBg)
		#self.imgBg = xbmcgui.ControlImage(0+x+pad,5*pad+y,w-2*pad,h-5*pad, os.path.join(mediaDir,'list-bg2.png'))
		#self.addControl(self.imgBg)
		
		# Title
		self.labelTitle = xbmcgui.ControlLabel(0+x, 0+y, w, hCnt, title, 'font14', '0xFFFFFFFF', alignment=2)
		self.addControl(self.labelTitle)
		
		self.cntList = xbmcgui.ControlList(2*pad+x, yo+y+3*pad, w-4*pad, h-10*pad, buttonFocusTexture = os.path.join(mediaDir,'button_focus.png'), font='font12', textColor='0xFFFFFFFF', space=0, itemHeight=7*pad)
		self.addControl(self.cntList)
		for item in items:
			self.cntList.addItem(str(item))
		self.setFocus(self.cntList)
		
	def onAction(self, action):
		if action == 10:
			self.selected = [-1, -1]
			self.close()
		elif action == 9: # Back
			self.selected = [-1, -1]
			self.close()	
		elif (action == 3) or (action == 4):
			try:	
				cnt = self.getFocus()
			except:
				self.setFocus(self.cntList)
				return None
		elif action == 7:
			if len(self.btns) != 0:
				popupMenu = popupBtns(title='', btns=self.btns, width=0.2)
				popupMenu.doModal()
				if popupMenu.selected != -1:
					self.selected = [popupMenu.selected, self.cntList.getSelectedPosition()]
					del popupMenu
					self.close()
				else:
					del popupMenu
			else:
				self.selected = [-1, self.cntList.getSelectedPosition()]
				self.close()
		else:
			pass
			
	def onControl(self, controlID):
		pass

"""
"""
		self.strActionInfo = xbmcgui.ControlLabel(100, 120, 200, 200, '', 'font13', '0xFFFF00FF')
		self.addControl(self.strActionInfo)
		self.strActionInfo.setLabel('Push BACK to quit')
		self.button0 = xbmcgui.ControlButton(250, 100, 80, 30, "HELLO")
		self.addControl(self.button0)
		self.button1 = xbmcgui.ControlButton(250, 200, 80, 30, "HELLO2")
		self.addControl(self.button1)
		self.button2 = xbmcgui.ControlButton(450, 200, 80, 30, "HELLO3")
		self.addControl(self.button2)
		self.setFocus(self.button0)
		self.button0.controlDown(self.button1)
		self.button1.controlUp(self.button0)
		self.button1.controlRight(self.button2)
		self.button2.controlLeft(self.button1)
"""
#class MyClass(xbmcgui.Window):
class MyClass(xbmcgui.WindowDialog):
	def __init__(self):
		self.texture = xbmcgui.ControlImage(0,0,537,154,"special://home/scripts/Texture.png")
		self.addControl(self.texture)

		self.strActionInfo = xbmcgui.ControlLabel(400, 190, 480, 20, '', 'font13', '0xFFFF00FF')
		self.addControl(self.strActionInfo)
		self.strActionInfo.setLabel('SynopsiTV Rating')
		#self.strActionInfo.setLabel('Please rate this movie.')

		self.button0 = xbmcgui.ControlButton(400, 210, 480, 20, "Skip")
		self.addControl(self.button0)
		
		self.button0 = xbmcgui.ControlButton(400, 230, 480, 20, "Skip")
		self.addControl(self.button0)
		
		self.button0 = xbmcgui.ControlButton(400, 250, 480, 20, "Skip")
		self.addControl(self.button0)
		

	def onAction(self, action):
		pass
		#if action == ACTION_PREVIOUS_MENU:
		#	self.close()

	def onControl(self, control):
		if control == self.button0:
			self.message('you pushed the 1st button')
		if control == self.button1:
			self.message('you pushed the 2nd button')
		if control == self.button2:
			self.message('you pushed the 3rd button')
	
	def message(self, message):
		dialog = xbmcgui.Dialog()
		dialog.ok(" My message title", message)
		self.close()


class XMLRatingDialog(xbmcgui.WindowXMLDialog):
	"""docstring for XMLRatingDialog"""
	def __init__( self, *args, **kwargs ):       
		pass
		
