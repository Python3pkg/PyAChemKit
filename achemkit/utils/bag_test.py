"""
This is the test harness for :py:mod:`achemkit.utils.bag`.

"""
#this will not be required once a proper installer exists
import sys
sys.path.append(".")

import unittest
from achemkit.utils.bag import *
try:
    import pickle as pickle
except ImportError:
    import pickle

class TestFrozenBag(unittest.TestCase):
    
    strrep = "FrozenBag((1, 1, 2, 3))"
    cls = FrozenBag
    
    def setUp(self):
        self.data = (1,2,1,3)
        self.bag = self.cls(self.data)
        self.bagb = self.cls(self.data)
        self.bag2 = self.cls(reversed(self.data))
        self.bag3 = self.cls(self.data+self.data)
        
    def test_len(self):
        self.assertEqual(len(self.bag), len(self.data))
        
    def test_iter(self):
        for a,b in zip(self.bag, sorted(self.data)):
            self.assertEqual(a, b)
        
    def test_hash(self):
        self.assertEqual(hash(self.bag), hash(self.bag2))
        self.assertEqual(hash(self.bag), hash(self.bagb))
        self.assertEqual(hash(self.cls(("B1", "B2"))), hash(self.cls(("B2", "B1"))))
        
    def test_str(self):
        self.assertEqual(str(self.bag), self.strrep)
        
    def test_repr(self):
        self.assertEqual(repr(self.bag), self.strrep)
        
    def test_eq(self):
        self.assertEqual(self.bag, self.bagb)
        self.assertNotEqual(self.bag, self.cls(self.data[:-1]))
        self.assertEqual(self.bag, self.bag2)
        self.assertNotEqual(self.bag, self.bag3)
        self.assertNotEqual(self.cls(("B1", "B1")), self.cls(("B1", "B2")))
        self.assertEqual(self.cls(("B1", "B2")), self.cls(("B2", "B1")))
        
    def test_pickle(self):
        pickstr = pickle.dumps(self.bag)
        newbag = pickle.loads(pickstr)
        self.assertEqual(self.bag, newbag)
        

class TestBag(TestFrozenBag):
    
    strrep = "Bag([1, 1, 2, 3])"
    cls = Bag
    
        
    def setUp(self):
        self.data = [1,2,1,3]
        self.bag = self.cls(self.data)
        self.bagb = self.cls(self.data)
        self.bag2 = self.cls(reversed(self.data))
        self.bag3 = self.cls(self.data+self.data)
        
    def test_hash(self):
        self.assertRaises(TypeError, hash, self.bag)
        
    def test_add(self):
        self.bag.add(4)
        self.assertEqual(self.bag, self.cls(reversed(self.data+[4])))
        
    def test_discard(self):
        self.bag.discard(2)
        self.data.remove(2)
        self.assertEqual(self.bag, self.cls(reversed(self.data)))

class TestOrderedFrozenBag(TestFrozenBag):
    
    strrep = "OrderedFrozenBag((1, 2, 1, 3))"
    cls = OrderedFrozenBag
    
    def setUp(self):
        super(TestOrderedFrozenBag, self).setUp()
        
    def test_iter(self):
        for a,b in zip(self.bag, self.data):
            self.assertEqual(a, b)

class TestOrderedBag(TestOrderedFrozenBag, TestBag):
    
    strrep = "OrderedBag([1, 2, 1, 3])"
    cls = OrderedBag

    def setUp(self):
        super(TestOrderedBag, self).setUp()
        
    def test_hash(self):
        self.assertRaises(TypeError, hash, self.bag)
