# coding=utf-8
import re
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


class SuperSubtitleAgentMovie(Agent.Movies):
    name = 'Feliratok.info'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.imdb']

    def search(self, results, media, lang, manual):
        show_id = SuperSubtitlesSearch.search_show(media.primary_metadata.title, media.primary_metadata.id)
        if show_id is not None:
            results.Append(MetadataSearchResult(id=show_id, score=100))

    def update(self, metadata, media, lang):
        for item in media.items:
            for part in item.parts:
                for lang in (Prefs['lang1'], Prefs['lang2']):
                    if lang == 'None':
                        continue
                    results = SuperSubtitlesSearch.get_movie_subtitles(metadata.id, lang)
                    result = SuperSubtitlesSearch.filter_subtitles(results, part.file)
                    if not result:
                        continue
                    subtitle = SuperSubtitlesSearch.download_subtitle(result.id)
                    if subtitle[0].split('.')[-1] != 'zip':
                        part.subtitles[languages[lang]][result.id] = Proxy.Media(subtitle[1], ext=subtitle[0].split('.')[-1])


class SuperSubtitleAgentTv(Agent.TV_Shows):
    name = 'Feliratok.info'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.thetvdb']

    def search(self, results, media, lang, manual):
        show_id = SuperSubtitlesSearch.search_show(media.primary_metadata.title, media.primary_metadata.id)
        if show_id is not None:
            results.Append(MetadataSearchResult(id=show_id, score=100))

    def update(self, metadata, media, lang):
        name_pattern = re.compile(r'^.* - (\d*)x(\d*) - .* \((.*)\).*')
        for s in media.seasons:
            for e in media.seasons[s].episodes:
                for item in media.seasons[s].episodes[e].items:
                    for part in item.parts:
                        for lang in (Prefs['lang1'], Prefs['lang2']):
                            if lang == 'None':
                                continue
                            results = SuperSubtitlesSearch.get_tv_subtitles(metadata.id, lang, s, e)
                            result = SuperSubtitlesSearch.filter_subtitles(results, part.file)
                            if not result:
                                continue
                            subtitle = SuperSubtitlesSearch.download_subtitle(result.id)
                            extension = subtitle[0].split('.')[-1]
                            if extension == 'zip':
                                zip_archive = Archive.Zip(subtitle[1])
                                for name in zip_archive:
                                    if name[-1] == '/':
                                        continue
                                    match = name_pattern.match(str(name))
                                    extension = str(name).split('.')[-1]
                                    if match and int(match.group(1)) == int(s) and int(match.group(2)) == int(e):
                                        part.subtitles[languages[lang]][result.id] = Proxy.Media(zip_archive[name], ext=extension)
                                        break
                            else:
                                part.subtitles[languages[lang]][result.id] = Proxy.Media(subtitle[1], ext=extension)