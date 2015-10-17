# coding=utf-8
import os
import io
import re
import subprocess
import search

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
        show_id = search.search_show(title, media.primary_metadata.id)
        if show_id is not None:
            results.Append(MetadataSearchResult(id=show_id, score=100))

    def update(self, metadata, media, lang):
        for item in media.items:
            for part in item.parts:
                for lang in (Prefs['lang1'], Prefs['lang2']):
                    if lang == 'None':
                        continue
                    results = search.get_movie_subtitles(metadata.id, lang)
                    result = search.filter_subtitles(results, part.file)
                    if not result:
                        continue
                    subtitle = search.download_subtitle(result.id)
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
        show_id = search.SearchShow(title, media.primary_metadata.id).search()
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
        results = search.get_tv_subtitles(metadata.id, language, season, episode)
        result = search.filter_subtitles(results, part.file)
        if not result:
            return
        subtitle = search.download_subtitle(result.id)
        extension = subtitle[0].split('.')[-1]
        lang = languages[language]
        if extension not in ['zip', 'rar']:
            part.subtitles[lang][result.id] = Proxy.Media(subtitle[1], ext=extension)
            return
        else:
            temp_dir, files = unpack(os.path.dirname(part.file), subtitle[1])
            found = []
            for name in files:
                match = self.episode_pattern.search(name)
                hit = match and match.group(1) is not None and int(match.group(1)) == int(season) and int(match.group(2)) == int(episode)
                hit = hit if hit else match and match.group(3) is not None and int(match.group(3)) == int(season) and int(match.group(4)) == int(episode)
                if hit:
                    found.append(name)
            if len(found) == 1:
                save_subtitle(part, lang, result.id, temp_dir+'/'+found[0])
            else:
                for name in found:
                    if search.check_version(name, part.file) is not None:
                        save_subtitle(part, languages[language], result.id, temp_dir+'/'+name)
            for item in files:
                os.remove(temp_dir+'/'+item)
            os.removedirs(temp_dir)


def unpack(directory, content):
    filename = directory + '/temp.rar'
    temp_dir = directory + '/temp'
    output = io.FileIO(filename, mode='w')
    output.write(content)
    output.flush()
    output.close()
    command = '/usr/local/bin/7z e -y -o' + temp_dir + ' ' + filename
    subprocess.check_output(command, shell=True)
    os.remove(filename)
    files = os.listdir(temp_dir)
    return temp_dir, files


def save_subtitle(part, language, result_id, path):
    subtitle_file = io.FileIO(path, mode='r')
    subtitle_data = subtitle_file.readall()
    subtitle_file.flush()
    subtitle_file.close()
    extension = path.split('.')[-1]
    part.subtitles[language][result_id] = Proxy.Media(subtitle_data, ext=extension)
