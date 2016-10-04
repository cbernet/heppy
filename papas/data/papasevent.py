''' Class to hold all the needed papas data collections
    This includes ...
    
'''

import pprint
#import copy
import collections 
import fnmatch
from heppy.papas.data.identifier import Identifier
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfalgo.distance import Distance
from heppy.papas.mergedclusterbuilder import MergedClusterBuilder
from heppy.framework.event import Event


class PapasEvent(Event):
    '''Builds the inputs to particle flow from a collection of simulated particles:
    - collects all smeared tracks and clusters
    - merges overlapping clusters 
    '''
    print_nstrip = 10 # ask colin
    
    def __init__(self):
        '''
        arguments
            
        '''
        self.collections = dict()
        self.history = dict()
        self.iEv = None
        
    def add_collection(self, collection):
        first = True
        collectiontype = None
        #work out the collectiontype from one of the identifiers and 
        #make sure 
        for id in collection.iterkeys():
            if first:
                collectiontype = Identifier.type_code(id)
                first =False
            if collectiontype != Identifier.type_code(id):
                assert "mixed types not allowed in a collection"
        self.collections[collectiontype] = collection
    
    def get_collection(self, type_code):
        return self.collections[type_code]
    
    def get_object(self, id):
        return self.collections[Identifier.type_code(id)][id]
    
      
    

   
   
   
    def lines(self):
        #approach copied from event.py and results used in printing this as part of event - improvements likely to be needed
        stripped_attrs = dict()
        for name, value in {"tracks" : self.tracks ,
                            "gen tracks" :self.gen_tracks ,
                            "ecal_clusters": self.ecal_clusters ,
                            "hcal_clusters": self.hcal_clusters ,
                            "gen_ecals": self.gen_ecals ,
                            "gen_hcals": self.gen_hcals ,
                            "smeared_hcals": self.smeared_ecals ,
                            "smeared_hcals": self.smeared_hcals ,
                            #"history": self.history ,
                            "sim_particles": self.sim_particles ,
                            "gen_stable_particles": self.gen_stable_particles }.iteritems() :
            stripped_attrs[name] = value
        for name, value in stripped_attrs.iteritems():
            if hasattr(value, '__len__') and len(value)>self.__class__.print_nstrip+1:
                # taking the first 10 elements and converting to a python list 
                # note that value could be a wrapped C++ vector
                if isinstance(value, collections.Mapping):
                    entries = [entry for entry in value.iteritems()]
                    entries = entries[:self.__class__.print_nstrip]
                    entries
                    stripped_attrs[name] = dict(entries)
                else:
                    stripped_attrs[name] = [ val for val in value[:self.__class__.print_nstrip] ]
                    stripped_attrs[name].append('...')
                    stripped_attrs[name].append(value[-1])    
        return stripped_attrs
                
    def __str__(self):
        header = 'PapasEvent:'
        stripped_attrs = self.lines()
        contents = pprint.pformat(stripped_attrs, indent=4)
        return '\n'.join([header, contents])
        
        
