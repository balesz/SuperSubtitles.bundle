# coding=utf-8
import re
import urllib
import httplib
from SuperSubtitlesParser import ResultParser
from SuperSubtitlesParser import DescriptionParser


def get_html_source(url, path, params=None):
        connection = httplib.HTTPConnection(url)
        if params is not None:
            connection.request("GET", "%s?%s" % (path, urllib.urlencode(params)))
        else:
            connection.request("GET", path)
        response = connection.getresponse()
        result = response.read()
        result = response.getheaders(), result
        connection.close()
        return result


def search_show(name, primary_id):
    params = dict(search=name)
    result = get_html_source('www.feliratok.info', '/index.php', params)
    parser = ResultParser(result[1])
    for item in parser.results:
        get_description(item)
        if item.tvdb_id == primary_id:
            return item.show_id
        if item.imdb_id == primary_id:
            return item.show_id
    return None


def get_description(item):
    params = dict(tipus='adatlap', azon='a_' + item.id)
    result = get_html_source('www.feliratok.info', '/index.php', params)
    DescriptionParser(item, result[1])


def get_movie_subtitles(show_id, language):
    params = dict(fid=show_id, nyelv=language)
    result = get_html_source('www.feliratok.info', '/index.php', params)
    parser = ResultParser(result[1])
    return parser.results


def get_tv_subtitles(show_id, language, season, episode):
    params = dict(sid=show_id, nyelv=language, evad=season, epizod1=episode, evadpakk='on')
    result = get_html_source('www.feliratok.info', '/index.php', params)
    parser = ResultParser(result[1])
    if len(parser.results) == 0:
        params.pop('evadpakk')
        result = get_html_source('www.feliratok.info', '/index.php', params)
        parser = ResultParser(result[1])
    return parser.results


def filter_subtitles(results, filename):
    subtitle_pattern = re.compile(r'^.*\((.*)\)?$')
    for result in results:
        versions = subtitle_pattern.match(result.name).group(1).split(', ')
        for version in versions:
            ver = version.replace(')', '').split('-')
            found = len(ver) > 0
            for v in ver:
                found = found and (v.lower() in str(filename).lower())
            if found:
                return result
    return None


def download_subtitle(show_id):
    params = dict(action='letolt', felirat=show_id)
    headers, result = get_html_source('www.feliratok.info', '/index.php', params)
    filename = None
    for header in headers:
        if 'filename=' in header[1]:
            filename = re.match(r'.* filename=\"(.*)\"', header[1]).group(1)
            break
    return filename, result