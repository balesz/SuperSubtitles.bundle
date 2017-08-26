import unittest
import re
import search


class MyTestCase(unittest.TestCase):

    def test1_tv(self):
        id = search.search_show("Dark matter", 'tt4159076')
        self.assertIsNotNone(id)

if __name__ == '__main__':
    unittest.main()
