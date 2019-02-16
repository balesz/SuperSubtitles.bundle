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


class MovieAgent:
    def search(self, metadata_id, title):
        show_id = search.search_show(title, metadata_id)
        return show_id

    def update(self, show_id, filename, langs):
        result = list()
        for lang in langs:
            subtitles = search.get_movie_subtitles(show_id, lang)
            subtitle = search.filter_subtitles(subtitles, filename)
            if not subtitle:
                continue
            subtitleFile = search.download_subtitle(subtitle.id)
            if subtitle.filename.split('.')[-1] != 'zip':
                result.append(tuple([subtitle.id, lang, subtitle.filename, subtitleFile]))
        return result
