import unittest

from billboard.utils import DroppingSet


class TestDroppingSet(unittest.TestCase):

    def test_add_discard(self):
        ds = DroppingSet(10)
        ds.add(4)
        ds.add(3)
        self.assertTrue(4 in ds)
        self.assertTrue(3 in ds)
        ds.discard(4)
        self.assertFalse(4 in ds)
        self.assertTrue(3 in ds)

    def test_order(self):
        ds = DroppingSet(10)
        ds.add(4)
        ds.add(3)
        ds.add(42)
        self.assertEqual(ds.pop(), 42)
        self.assertEqual(ds.pop(), 3)
        self.assertEqual(ds.pop(), 4)

    def test_max(self):
        ds = DroppingSet(4)
        ds.add(1)
        ds.add(2)
        ds.add(3)
        ds.add(4)
        self.assertTrue(1 in ds)
        self.assertTrue(4 in ds)
        ds.add(5)
        self.assertFalse(1 in ds)
        self.assertTrue(2 in ds)
        self.assertTrue(4 in ds)
        self.assertTrue(5 in ds)
        ds.add(6)
        self.assertFalse(2 in ds)
