import unittest
import itertools
from idcoder import IdCoder 

class TestIdentifier(unittest.TestCase):

    def test_identifier(self):
        IdCoder.reset()
        uid = IdCoder.make_id(IdCoder.PFOBJECTTYPE.TRACK, 0, 's', 1.23456)
        id1 = IdCoder.make_id(IdCoder.PFOBJECTTYPE.TRACK, 1, 's', 12.782) 
       
        self.assertTrue (IdCoder.pretty(id1) == 'ts1')
        ids = []
        for i in range(0, 5) :
            uid = IdCoder.make_id(IdCoder.PFOBJECTTYPE.TRACK, i , 's', 2**(i-2) )
            ids.append(uid)
        ids = sorted(ids, reverse = True)
        self.assertTrue(IdCoder.pretty(ids[0]) == 'ts4')
        self.assertTrue(IdCoder.get_value(ids[0]) == 4.0)
        self.assertTrue(IdCoder.pretty(ids[3]) == 'ts1')
        self.assertTrue(IdCoder.get_value(ids[3]) == 0.5)        

if __name__ == '__main__':
    unittest.main()



