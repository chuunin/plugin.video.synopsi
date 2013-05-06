
class SynopsiMovieAgent(Agent.Movies):

	name = 'Synopsi Agent'
	languages = [
		Locale.Language.English,
	]

	primary_provider = True
	fallback_agent = None
	accepts_from = None
	contributes_to = None


	def search(self, results, media, lang, manual=False):

		Log.Debug('XXX %s %s' % (media.filename, media.name))



		# result = MetadataSearchResult(

		# 	)

		# results.Append(result)

	def update(self, metadata, media, lang, force):
		metadata.title = 'ZZZ ' + str(media)
		Log.Warn('XXXX  update %s' % media)
