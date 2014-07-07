import unittest


class MyTestCase(unittest.TestCase):

    def test_tv(self):
        id = SuperSubtitlesSearch.search_show("Defiance", '255326')
        print(id)

    def test_movie(self):
        id = SuperSubtitlesSearch.search_show("Leaving las vegas", '0113627')
        print(id)


if __name__ == '__main__':
    unittest.main()
