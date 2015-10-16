import unittest
import re
import search


class MyTestCase(unittest.TestCase):

    def test1_tv(self):
        id = search.search_show("Defiance", '255326')
        print(id)

    def test2_movie(self):
        id = search.search_show("Leaving las vegas", 'tt0113627')
        print(id)

    def test3_regexp(self):
        regexp = re.compile(r'((\d+)x(\d+)|s(\d+)e(\d+))', re.I)
        match = regexp.search('The Strain - 01x01 - Night Zero.DIMENSION.Eng.srt')
        if match:
            print(match.groups())
        match = regexp.search('The.Strain.S01E01.HDTV.XviD-FUM.srt')
        if match:
            print(match.groups())


if __name__ == '__main__':
    unittest.main()
