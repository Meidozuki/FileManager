import unittest
import os,sys

sys.path.append(os.path.abspath('..'))

from src.table_item import TableItem

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
