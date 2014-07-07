# coding=utf-8
import re
from HTMLParser import HTMLParser


def clear_html(value):
    start_pattern = "<!--Az eredménytáblázat ELEJE-->"
    end_pattern = "<!--Az eredménytáblázat VÉGE-->"
    if value.find(start_pattern) > 0 and value.find(end_pattern) > 0:
        return value[value.find(start_pattern):value.find(end_pattern) + len(end_pattern)]
    return value


class SubtitleInfo:
    def __init__(self):
        self.id = None
        self.name = None
        self.is_movie = False
        self.show_id = None
        self.imdb_id = None
        self.tvdb_id = None


# noinspection PyAugmentAssignment
class ResultParser(HTMLParser):
    def __init__(self, raw):
        HTMLParser.__init__(self)
        self.level = 0
        self.data = None
        self.processing = False
        self.need_reading_data = False
        self.results = []
        self.subtitle = None
        self.feed(clear_html(raw))

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.level = self.level + 1
            for attr in attrs:
                if attr == ("id", "vilagit"):
                    self.subtitle = SubtitleInfo()
                    self.level = 1
                    self.processing = True
        if self.processing:
            if tag == "a":
                self.get_show_id(attrs[0][1])
                self.get_subtitle_id(attrs[0][1])
            if tag == "div" and attrs[0] == ("class", "eredeti"):
                self.data = ""
                self.need_reading_data = True

    def handle_data(self, data):
        if self.need_reading_data:
            self.data = self.data + data

    def handle_endtag(self, tag):
        if tag == "div" and self.need_reading_data:
            self.get_name(self.data)
            self.data = None
            self.need_reading_data = False
        if tag == "tr":
            if self.processing and self.level > 0:
                self.level = self.level - 1
            if self.processing and self.level == 0:
                self.results.append(self.subtitle)
                self.subtitle = None
                self.processing = False

    def get_name(self, value):
        self.subtitle.name = value

    def get_show_id(self, value):
        match = re.search(r'index\.php\?([fs]id)=(\d*)', value)
        if match:
            self.subtitle.is_movie = match.group(1) == 'fid'
            self.subtitle.show_id = match.group(2)

    def get_subtitle_id(self, value):
        match = re.search(r'/index\.php\?action=letolt&fnev=.*&felirat=(\d*)', value)
        if match:
            self.subtitle.id = match.group(1)


class DescriptionParser(HTMLParser):
    metadata = SubtitleInfo()

    def __init__(self, metadata, description):
        HTMLParser.__init__(self)
        self.metadata = metadata
        self.feed(clear_html(description))

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and len(attrs) == 3 and attrs[2] == ('alt', 'iMDB'):
            match = re.search('^.*/tt(\d*)/?$', attrs[0][1])
            if match:
                self.metadata.imdb_id = match.group(1)
        if tag == 'a' and len(attrs) == 3 and attrs[2] == ('alt', 'TheTVDB'):
            match = re.search('^.*id=(\d*)$', attrs[0][1])
            if match:
                self.metadata.tvdb_id = match.group(1)