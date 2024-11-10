import unittest

class ExampleTestStrings1(unittest.TestCase):

    def test_add(self):
        """ Test the addition of two numbers within motor board """
        self.assertEqual(1 + 1, 2)
        self.assertEqual(-1 + 1, 0)
    
