# coding=utf-8
import urllib
import httplib
from parser import *


def get_html_source(url, path, params=None):
    context = httplib.ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = httplib.ssl.CERT_NONE
    connection = httplib.HTTPSConnection(url, context=context)
    if params is not None:
        connection.request("GET", "%s?%s" % (path, urllib.urlencode(params)))
    else:
        connection.request("GET", path)
    response = connection.getresponse()
    result = response.read()
    result = response.getheaders(), result
    connection.close()
    return result


class SearchShow:
    def __init__(self, title, primary_id):
        self.title = str(title)
        self.primary_id = str(primary_id)

    def search(self):
        result = search_show(self.title, self.primary_id)
        if result is None:
            for segment in self.title.split(' '):
                result = search_show(segment, self.primary_id)
                if result is not None:
                    return result
        return result


def search_show(search, primary_id):
    params = dict(search=search)
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
    version_pattern = re.compile(r'^.*\((.*)\)?$')
    for result in results:
        versions = version_pattern.match(result.name).group(1).split(', ')
        for version in versions:
            ver = version.replace(')', '').split('-')
            found = len(ver) > 0
            for v in ver:
                found = found and (v.lower() in str(filename).lower())
            if not found:
                found = ver[-1].lower() in str(filename).lower()
            if found:
                return result
    return None


def check_version(subtitle, filename):
    version_pattern = re.compile(r'^.*\((.*)\).*$')
    versions = version_pattern.match(subtitle).group(1).split(', ')
    for version in versions:
        ver = version.replace(')', '').split('-')
        found = len(ver) > 0
        for v in ver:
            found = found and (v.lower() in str(filename).lower())
        if not found:
            found = ver[-1].lower() in str(filename).lower()
        if found:
            return subtitle
    return None


def download_subtitle(subtitle_id):
    params = dict(action='letolt', felirat=subtitle_id)
    headers, result = get_html_source('www.feliratok.info', '/index.php', params)
    return result