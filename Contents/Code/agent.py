
class SynopsiMovieAgent(Agent.Movies):

	name = 'Synopsi Agent'
	languages = [
		Locale.Language.English,
	]

	primary_provider = True
	fallback_agent = False
	accepts_from = None
	contributes_to = None


def search(self, results, media, lang, manual):
	Log.Info('search %s' % media)

def update(self, metadata, media, lang, force):
	Log.Info('update %s' % media)
