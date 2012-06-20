import xbmc, xbmcgui
import os
import lib

CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )
#CANCEL_DIALOG  = ( 9, 92, 216, 247, 257, 275, 61467, 61448, )

class XMLRatingDialog(xbmcgui.WindowXMLDialog):
	"""docstring for XMLRatingDialog"""
	def __init__( self, *args, **kwargs ):
		self.data = {'type': "rating"}
		self.data['current time'] = kwargs['ctime']
		self.data['total time'] = kwargs['tottime']
		self.token = kwargs['token']
		#xbmc.log(str(args))
		#xbmc.log("SynopsiTV: Prepare to send. " + str(curtime) + " "+ str(totaltime))
	def message(self, message):
		dialog = xbmcgui.Dialog()
		dialog.ok(" My message title", message)
		self.close()
	def onInit( self ):
		pass
	def onClick( self, controlId ):
		if controlId == 11:
			xbmc.log("SynopsiTV: Rated Amazing")
			self.data['rating']  = "Amazing"
		elif controlId == 10:
			xbmc.log("SynopsiTV: Rated OK")
			self.data['rating']  = "OK"
		elif controlId == 15:
			xbmc.log("SynopsiTV: Rated Terrible")
			self.data['rating']  = "Terrible"
		else:
			xbmc.log("SynopsiTV: Not Rated")
			self.data['rating']  = "Not Rated"
		lib.send_data(self.data,self.token)


		self.close()
	def onFocus( self, controlId ):
		self.controlId = controlId

	def onAction( self, action ):
		if ( action.getId() in CANCEL_DIALOG):
			xbmc.log("SynopsiTV: Not Rated")
			self.data['rating']  = "Not Rated"
			lib.send_data(self.data,self.token)
			self.close()
		#if action.getId() == 11:
		#	self.message('Ty vole stlacils 11')

		
