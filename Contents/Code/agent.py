
class SynopsiMovieAgent(Agent.Movies):

	name = 'Synopsi Agent'
	languages = [
		Locale.Language.English,
	]

	primary_provider = True
	fallback_agent = None
	accepts_from = None
	contributes_to = None


def search(self, results, media, lang):
	Log.Warn('XXXX search %s' % media)

def update(self, metadata, media, lang, force):
	metadata.title = media
	Log.Warn('XXXX  update %s' % media)
