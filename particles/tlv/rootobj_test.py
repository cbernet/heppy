import unittest
import copy
from itertools import count 

from rootobj import RootObj

class RootObjTestCase(unittest.TestCase):

    def test_instance_id(self):
        RootObj._ids = count(0)
        class T1(RootObj):
            pass
        class T2(RootObj):
            pass
        t1 = T1()
        t1_2 = T1()
        self.assertEqual(t1.objid, 0)
        self.assertEqual(t1_2.objid, 1)
        t2 = T2()
        self.assertEqual(t2.objid, 2)

    def test_equality(self):
        RootObj._ids = count(0)
        class T1(RootObj):
            pass
        t1 = T1()
        self.assertEqual(t1.objid, 0)
        t1_2 = copy.deepcopy(t1)
        self.assertEqual(t1_2.objid, 0)
        self.assertEqual(t1_2, t1)
        self.assertTrue(t1_2 in [t1])
        
        
if __name__ == '__main__':
    unittest.main()        
    
