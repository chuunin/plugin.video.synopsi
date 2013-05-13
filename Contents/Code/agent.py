
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

		astv_hash = stv_hash(media.filename)

		ident = {
			'file_name': media.filename,	# todo: send relative path only
			'os_title_hash': media.openSubtitlesHash,
			'stv_title_hash': astv_hash,
			'total_time': media.duration,
			'label': media.name,
		}

		ident_results = apiclient.titleIdentify(**ident)

		Log.Debug('identified:' + str(ident_results))
		# result = MetadataSearchResult(
		# 	)
		# results.Append(result)

	def update(self, metadata, media, lang, force):
		metadata.title = 'ZZZ ' + str(media)
		Log.Warn('XXXX  update %s' % media)
