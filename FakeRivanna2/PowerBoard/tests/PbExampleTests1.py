import unittest

from Testing_Library.gpio import DigitalInput


class ExampleTestStrings1(unittest.TestCase):

    def test_add(self):
        """ Test the addition of two numbers within power board """
        self.assertEqual(1 + 1, 2)
        self.assertEqual(-1 + 1, 0)
        print("\n\nConfig file from within the power board tests: ", self.config_data)
    
    def test_subtract(self):
        """ Test the subtraction of two numbers within power board """
        self.assertEqual(1 - 1, 0)
        self.assertEqual(-1 - 1, -2)
        self.assertEqual(5 - 1, 4)
    
    def test_gpio_pin_creation(self):
        """ Test the creation of a GPIO pin within power board """
        pin = DigitalInput("GPIO2")
        self.assertEqual(pin.pinName, "GPIO2")
        self.assertEqual(pin.pinNumber, 2)