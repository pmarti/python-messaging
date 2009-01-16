import unittest
from messaging.test.test_encoding import TestEncodingFunctions

suite = unittest.TestLoader().loadTestsFromTestCase(TestEncodingFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)


