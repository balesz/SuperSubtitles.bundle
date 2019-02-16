# coding=utf-8
import os
import io
import re
import subprocess
import agent
import search


class AgentMovie(Agent.Movies):
    name = 'Feliratok.info'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.imdb']
    feliratokAgent = agent.MovieAgent()

    def search(self, results, media, lang, manual):
        title = media.primary_metadata.title
        metadata_id = media.primary_metadata.id
        show_id = self.feliratokAgent.search(metadata_id, title)
        if show_id is not None:
            results.Append(MetadataSearchResult(id=show_id, score=100))

    def update(self, metadata, media, lang):
        langs = [Prefs['lang1'], Prefs['lang2']]
        langs = [lang for lang in langs if lang != 'None' and lang is not None]
        parts = [part for item in media.items for part in item.parts]
        for part in parts:
            results = self.feliratokAgent.update(metadata.id, part.file, langs)
            for primary_id, lang, filename, subtitle in results:
                part.subtitles[agent.languages[lang]][primary_id] = Proxy.Media(subtitle, ext=filename.split('.')[-1])


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
        extension = result.filename.split('.')[-1]
        lang = agent.languages[language]
        if extension not in ['zip', 'rar']:
            part.subtitles[lang][result.id] = Proxy.Media(subtitle, ext=extension)
            return
        else:
            temp_dir, files = unpack(os.path.dirname(part.file), subtitle)
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
                        save_subtitle(part, agent.languages[language], result.id, temp_dir+'/'+name)
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
