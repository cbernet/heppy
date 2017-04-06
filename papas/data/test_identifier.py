import unittest
import itertools
from identifier import Identifier 

class TestIdentifier(unittest.TestCase):

    def test_identifier(self):
        Identifier.reset()
        uid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 0, 's', 1.23456)
        id1 = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 1, 's', 12.782) 
       
        self.assertTrue (Identifier.pretty(id1) == 'ts1')
        ids = []
        for i in range(0, 5) :
            uid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, i , 's', 2**(i-2) )
            ids.append(uid)
        ids = sorted(ids, reverse = True)
        self.assertTrue(Identifier.pretty(ids[0]) == 'ts4')
        self.assertTrue(Identifier.get_value(ids[0]) == 4.0)
        self.assertTrue(Identifier.pretty(ids[3]) == 'ts1')
        self.assertTrue(Identifier.get_value(ids[3]) == 0.5)        

if __name__ == '__main__':
    unittest.main()



