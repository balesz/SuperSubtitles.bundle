# coding=utf-8
from fileinput import filename
import SuperSubtitlesSearch


languages = {
    "None": "None",
    "Magyar": "hu",
    "Angol": "en",
    "Albán": "sq",
    "Arab": "ar",
    "Bolgár": "bg",
    "Cseh": "cs",
    "Dán": "da",
    "Finn": "fi",
    "Francia": "fr",
    "Görög": "el",
    "Héber": "he",
    "Holland": "nl",
    "Horvát": "co",
    "Koreai": "ko",
    "Lengyel": "pl",
    "Német": "de",
    "Norvég": "no",
    "Olasz": "it",
    "Orosz": "ru",
    "Portugál": "pt",
    "Román": "ro",
    "Spanyol": "es",
    "Svéd": "sv",
    "Szerb": "sr",
    "Szlovén": "sl",
    "Szlovák": "sk",
    "Török": "tr"
}


def Start():
    Log('########## Start ##########')


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
                        results = SuperSubtitlesSearch.get_tv_subtitles(metadata.id, lang1, s, e)
                        result = SuperSubtitlesSearch.filter_subtitles(results, part.file)
                        if not result:
                            continue
                        subtitle = SuperSubtitlesSearch.download_subtitle(result.id)
                        if subtitle[0].split('.')[-1] != 'zip':
                            Log(subtitle[0])
                            part.subtitles[languages[lang1]][result.id] = Proxy.Media(subtitle[1], ext=subtitle[0].split('.')[-1])