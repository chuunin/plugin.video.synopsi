import xbmc, xbmcgui
import os


CANCEL_DIALOG  = ( 9, 10, 92, 216, 247, 257, 275, 61467, 61448, )

class XMLRatingDialog(xbmcgui.WindowXMLDialog):
	"""docstring for XMLRatingDialog"""
	self.data = {}
	def __init__( self, *args, **kwargs ):
		self.ctime = kwargs['ctime']
		self.tottime = kwargs['tottime']
		#xbmc.log(str(args))
		#xbmc.log("SynopsiTV: Prepare to send. " + str(curtime) + " "+ str(totaltime))
	def message(self, message):
		dialog = xbmcgui.Dialog()
		dialog.ok(" My message title", message)
		self.close()
	def onInit( self ):
		pass
	def onClick( self, controlId ):
		pass
		if controlId == 11:
			xbmc.log("SynopsiTV: Rated Amazing")
		elif controlId == 10:
			xbmc.log("SynopsiTV: Rated OK")
		elif controlId == 15:
			xbmc.log("SynopsiTV: Rated Terrible")


		self.close()
	def onFocus( self, controlId ):
		self.controlId = controlId

	def onAction( self, action ):
		if ( action.getId() in CANCEL_DIALOG):
			self.close()
		#if action.getId() == 11:
		#	self.message('Ty vole stlacils 11')

		
