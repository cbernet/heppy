import unittest
import itertools
from identifier import Identifier 

class TestIdentifier(unittest.TestCase):

    def test_identifier(self):
        Identifier.reset()
        uid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 1.23456)
        id1 = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 12.782) 
       
        self.assertTrue (Identifier.pretty(id1) == 'ts2')
        ids = []
        for i in range(-2, 2):
            uid = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, 's', 2**(i) )
            ids.append(uid)
        ids = sorted(ids, reverse = True)
        self.assertTrue(Identifier.pretty(ids[0]) == 'ts6')
        self.assertTrue(Identifier.get_value(ids[0]) == 2.0)
        self.assertTrue(Identifier.pretty(ids[3]) == 'ts3')
        self.assertTrue(Identifier.get_value(ids[3]) == 0.25)        

if __name__ == '__main__':
    unittest.main()



