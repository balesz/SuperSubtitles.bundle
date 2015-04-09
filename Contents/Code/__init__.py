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
        title = media.primary_metadata.title
        show_id = SuperSubtitlesSearch.search_show(title, media.primary_metadata.id)
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

    episode_pattern = re.compile(r'(\d+)x(\d+)|s(\d+)e(\d+)', re.I)

    def search(self, results, media, lang, manual):
        title = media.primary_metadata.title
        title = re.sub(r'(.*) \(.*\)', r'\1', title)
        show_id = SuperSubtitlesSearch.search_show(title, media.primary_metadata.id)
        if show_id is not None:
            results.Append(MetadataSearchResult(id=show_id, score=100))

    def update(self, metadata, media, lang):
        for s in media.seasons:
            for e in media.seasons[s].episodes:
                for item in media.seasons[s].episodes[e].items:
                    for part in item.parts:
                        for lang in (Prefs['lang1'], Prefs['lang2']):
                            self.update_part(lang, metadata, media, s, e, part)

    def update_part(self, language, metadata, media, season, episode, part):
        if language == 'None':
            return
        results = SuperSubtitlesSearch.get_tv_subtitles(metadata.id, language, season, episode)
        result = SuperSubtitlesSearch.filter_subtitles(results, part.file)
        if not result:
            return
        subtitle = SuperSubtitlesSearch.download_subtitle(result.id)
        extension = subtitle[0].split('.')[-1]
        if extension == 'zip':
            zip_archive = Archive.Zip(subtitle[1])
            zip_results = []
            file_count = 0
            for name in zip_archive:
                file_count += 1
                extension = str(name).split('.')[-1]
                if name[-1] == '/' or extension != 'srt':
                    continue
                match = self.episode_pattern.search(str(name))
                hit = match and match.group(1) is not None and int(match.group(1)) == int(season) and int(match.group(2)) == int(episode)
                hit = hit if hit else match and match.group(3) is not None and int(match.group(3)) == int(season) and int(match.group(4)) == int(episode)
                if hit:
                    zip_results.append(name)
            if len(zip_results) == 1:
                part.subtitles[languages[language]][result.id] = Proxy.Media(zip_archive[zip_results[0]], ext=extension)
            else:
                for name in zip_results:
                    if SuperSubtitlesSearch.check_version(name, part.file) is not None:
                        part.subtitles[languages[language]][result.id] = Proxy.Media(zip_archive[name], ext=extension)

        else:
            part.subtitles[languages[language]][result.id] = Proxy.Media(subtitle[1], ext=extension)