import unittest

class ExampleTestStrings1(unittest.TestCase):

    def test_string_split(self):
        """ Test splitting strings within power board """
        self.assertEqual("hixhi".split("x"), ["hi", "hi"])
