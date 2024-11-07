import unittest
import argparse
import tests.ExampleTestStrings

def make_suite():
    # OLD VERSION (if you want only specific tests): 
    # embedded_tests = [ExampleTestStrings("test_add"), ExampleTestStrings("test_subtract")]

    # NEW VERSION (if you want all tests in the ExampleTestStrings.py file):
    loader = unittest.TestLoader()
    return loader.loadTestsFromModule(tests.ExampleTestStrings)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run test suite with optional verbosity.")
    parser.add_argument(
        "-v", "--verbosity", 
        type=int, 
        choices=[0, 1, 2], 
        default=1,
        help="Set verbosity level (0, 1, or 2). Default is 1."
    )
    args = parser.parse_args()

    suite = make_suite()
    runner = unittest.TextTestRunner(verbosity=args.verbosity)
    runner.run(suite)


