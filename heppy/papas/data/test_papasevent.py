import unittest
import itertools
import copy

from heppy.papas.data.idcoder import IdCoder
from papasevent import PapasEvent 

class TestPapasEvent(unittest.TestCase):
    def test_papasevent(self):
        papasevent = PapasEvent(0)
        ecals = dict()
        tracks = dict()
        mixed = dict()

        for i in range(0, 2):
            uid = IdCoder.make_id(IdCoder.PFOBJECTTYPE.ECALCLUSTER, i,'t', 4.5)
            ecals[uid] = uid
        for i in range(0, 2):
            uid = IdCoder.make_id(IdCoder.PFOBJECTTYPE.TRACK, i, 's', 4.5)
            tracks[uid] = uid            
        
        lastid = IdCoder.make_id(IdCoder.PFOBJECTTYPE.ECALCLUSTER, 3, 't', 3)
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
        self.assertTrue( len(papasevent.get_collection('zz')) == 0 )  # this one does not exist 
        self.assertTrue( len(papasevent.get_collection('et'))  == 3 )
        
        #check get_object
        self.assertTrue( IdCoder.pretty(papasevent.get_object(lastid))  == 'et3' )
        self.assertTrue( papasevent.get_object(499)  is None )       

if __name__ == '__main__':
    unittest.main()
