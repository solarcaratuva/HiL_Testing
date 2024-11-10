import unittest

class ExampleTestStrings1(unittest.TestCase):

    def test_add(self):
        """ Test the addition of two numbers within power board """
        self.assertEqual(1 + 1, 2)
        self.assertEqual(-1 + 1, 0)
    
    def test_subtract(self):
        """ Test the subtraction of two numbers within power board """
        self.assertEqual(1 - 1, 0)
        self.assertEqual(-1 - 1, -2)
        self.assertEqual(5 - 1, 4)