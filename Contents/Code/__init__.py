# coding=utf-8
import SuperSubtitlesSearch


def Start():
    Log('Start')


class SuperSubtitleAgentMovie(Agent.Movies):
    name = 'Feliratok.info'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.imdb']

    def search(self, results, media, lang, manual):
        Log('########## Movie Search ##########')

    def update(self, metadata, media, lang):
        Log('########## Movie Update ##########')


class SuperSubtitleAgentTv(Agent.TV_Shows):
    name = 'Feliratok.info'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.thetvdb']

    def search(self, results, media, lang, manual):
        show_id = SuperSubtitlesSearch.search_show(media.primary_metadata.title, media.primary_metadata.id)
        results.Append(MetadataSearchResult(id=show_id, score=100))

    def update(self, metadata, media, lang):
        lang1 = Prefs['lang1']
        for s in media.seasons:
            for e in media.seasons[s].episodes:
                for item in media.seasons[s].episodes[e].items:
                    for part in item.parts:
                        if 'hu' not in part.subtitles.keys():
                            results = SuperSubtitlesSearch.get_tv_subtitles(metadata.id, lang1, s, e)
                            result = SuperSubtitlesSearch.filter_subtitles(results, part.file)
                            if result:
                                filename, data = SuperSubtitlesSearch.download_subtitle(result.id)
                                Log(filename)
                                part.subtitles['hu'][result.id] = Proxy.Media(data, ext=filename.split('.')[-1])