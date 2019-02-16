import unittest
import re
import agent


class MovieAgentTestCase(unittest.TestCase):
    feliratokAgent = agent.MovieAgent()

    metadata_id = 'tt4530422'
    title = 'Overlord'
    filename = 'Overlord.2018.720p.AMZN.WEBRip.DDP5.1.x264-NTG/Overlord.2018.720p.AMZN.WEB-DL.DDP5.1.H.264-NTG.mkv'
    langs = ['Magyar', 'Angol']

    def test_search(self):
        primary_id = self.feliratokAgent.search(self.metadata_id, self.title)
        self.assertIsNotNone(primary_id)
        print(primary_id)
    
    def test_update(self):
        show_id = self.feliratokAgent.search(self.metadata_id, self.title)
        results = self.feliratokAgent.update(show_id, self.filename, self.langs)
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)
        print(list(map(lambda it: tuple([it[0], it[1], it[2]]), results)))


if __name__ == '__main__':
    unittest.main()
