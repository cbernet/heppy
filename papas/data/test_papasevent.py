import unittest
import itertools
import copy

from heppy.papas.data.identifier import Identifier
from papasevent import PapasEvent 

class TestPapasEvent(unittest.TestCase):

    def test_papasevent(self):
        papasevent = PapasEvent(0)
        ecals = dict()
        tracks = dict()
        mixed = dict()

        for i in range(0, 2):
            uid = Identifier.make_id(Identifier.PFOBJECTTYPE.ECALCLUSTER, 't', 4.5)
            ecals[uid] = uid
            uid = Identifier.make_id(Identifier.PFOBJECTTYPE.ECALCLUSTER, 's', 4.5)
            tracks[uid] = uid            
        
        lastid = Identifier.make_id(Identifier.PFOBJECTTYPE.ECALCLUSTER, 't', 3)
        ecals[lastid] = lastid    
        
        papasevent.add_collection(ecals)
        papasevent.add_collection(tracks)
        
        #check that adding the same collection twice fails        
        self.assertRaises(ValueError, papasevent.add_collection, ecals)
        
        #check that adding a mixed collection fails
        mixed = ecals.copy()
        mixed.update(tracks)
        self.assertRaises(ValueError, papasevent.add_collection, mixed)
        
        #get we can get back collections OK
        self.assertTrue( papasevent.get_collection('zz') is None)
        self.assertTrue( len(papasevent.get_collection('et'))  == 3 )
        
        #check get_object
        self.assertTrue( Identifier.pretty(papasevent.get_object(lastid))  == 'et5' )
        self.assertTrue( papasevent.get_object(499)  is None )       

if __name__ == '__main__':
    unittest.main()
