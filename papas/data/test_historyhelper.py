import unittest
import itertools
import copy
from identifier import Identifier
from papasevent import PapasEvent 
from historyhelper import HistoryHelper
from heppy.papas.graphtools.DAG import Node

class TestHistoryHelper(unittest.TestCase):

    def test_papasevent(self):
        
        #create a dummy papasevent
        papasevent = PapasEvent(0)
        ecals = dict()
        tracks = dict()
        mixed = dict()
        
        for i in range(0, 2):
            uid = Identifier.make_id(Identifier.PFOBJECTTYPE.ECALCLUSTER, i, 't', 4.5)
            ecals[uid] = uid
            papasevent.history[uid] = Node(uid)
            uidt = Identifier.make_id(Identifier.PFOBJECTTYPE.TRACK, i, 's', 4.5)
            tracks[uidt] = uidt  
            papasevent.history[uidt] = Node(uidt)
            papasevent.history[uidt].add_child(papasevent.history[uid])

        lastid = Identifier.make_id(Identifier.PFOBJECTTYPE.ECALCLUSTER, 3, 't', 3)
        ecals[lastid] = lastid   
        papasevent.history[lastid] = Node(lastid)
        papasevent.add_collection(ecals)
        papasevent.add_collection(tracks)
        
        #create HistoryHelper
        hhelper =  HistoryHelper(papasevent)
        
        #get all ids in event
        ids =  hhelper.event_ids()
        self.assertTrue(len(ids) == 5)

        #check id_from_pretty
        self.assertTrue(hhelper.id_from_pretty('et3') == lastid)
        
        #check get_linked_ids
        
        linked = hhelper.get_linked_ids(lastid) #everything linked to lastid (which is just lastid)
        self.assertTrue(linked[0] == lastid and len(linked) == 1)        
        self.assertTrue( hhelper.get_linked_ids( ids[0], direction="undirected")[1] == hhelper.id_from_pretty('ts0'))
        self.assertTrue( hhelper.get_linked_ids( ids[0], direction="parents")== hhelper.get_linked_ids( ids[0], direction="undirected"))
        self.assertTrue( hhelper.get_linked_ids(ids[0], direction="children") == [hhelper.id_from_pretty('et0')])
        
        #filter_ids
        self.assertTrue( len(hhelper.filter_ids(ids, 'ts')) == 2)
        self.assertTrue( hhelper.filter_ids(ids, 'no') == [])
        
        #get_collection
        self.assertTrue( len( hhelper.get_collection(ids[1:2], 'no'))  == 0)
        self.assertTrue( len( hhelper.get_collection([99], 'no'))  == 0)
        self.assertTrue( len(hhelper.get_collection(ids[0:2], 'ts')) == 1)
        pass
    
        #get_history_subgroups
        subgroups = hhelper.get_history_subgroups()
        self.assertTrue(len(subgroups) == 3)
        
        #get_linked_collection
        self.assertTrue(hhelper.get_linked_collection( hhelper.id_from_pretty('et0'), 'ts').keys() == [hhelper.id_from_pretty('ts0')])
        self.assertRaises(KeyError, hhelper.get_linked_collection, 0, 'ts')
        self.assertTrue(len(hhelper.get_linked_collection( hhelper.id_from_pretty('et0'), 'no')) == 0)
        

if __name__ == '__main__':
    unittest.main()
