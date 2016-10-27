from heppy.papas.data.identifier import Identifier
from heppy.framework.event import Event


class PapasEvent(Event):
    ''' Contains all the papas event data eg smeared tracks, merged ecal clusters, reconstructed particles etc
        together with the history whcih descibes the linkages between the data
        The collections and history are required to match perfectly,
        ie if in identifier is in the history it will be in one of the collections and vice versa

        The collections dict object contains dicts, one dict per object type,
        eg all smeared_ecals in the papasevent will be stored as one dict inside the collections.
        
        The type_and_subtype is used to label the collections in the papasevent
        it is a two letter code formed out of 'type' + 'subtype'
        For example
          'pr' is particle that has reconstructed subtype
          'es' contains ecals that are smeared

        Type codes
                      e = ecal
                      h = hcal
                      t = track
                      p = particle

        Subtype codes are a single letter, current usage includes:
             'g' generated
             'm' merged
             'r' reconstructed
             'u' unspecified
             't' true
             's' simulated (particles)
                 smeared (tracks ecals hcals)
                 split (blocks)
                 
        Usage:

        papasevent.add_collection(true_ecals)
        smeared_ecals=papasevent.get_collection('es')  
    '''
    
    def __init__(self):
        super(PapasEvent, self).__init__(self)
        self.collections = dict()
        self.history = dict()
        self.iEv = None
        
    def add_collection(self, collection):
        '''Add a new collection into the PapasEvent. The collection should contain only one object type
           and only one collection of each type should be stored in the PapasEvent        
        '''
        first = True
        collectiontype = None
        #make sure everything is the same type
        for id in collection.iterkeys():
            if first:
                collectiontype = Identifier.type_and_subtype(id)
                if collectiontype in self.collections.keys():
                    assert "Collection Type must be unique"
                first = False
            if collectiontype != Identifier.type_and_subtype(id):
                assert "mixed types not allowed in a collection"
        self.collections[collectiontype] = collection
    
    def get_collection(self, type_and_subtype):
        return self.collections[type_and_subtype]

    def get_object(self, id):
        '''get an object corresponding to a unique id'''
        collection = self.get_collection(Identifier.type_and_subtype(id))
        if collection.has_key(id):      
            return self.collections[Identifier.type_and_subtype(id)][id]
        assert "id was not found in collection"
    
    def get_objects(self, ids, type_and_subtype):
        ''' ids must all be of type type_and_subtype
        get a dict of objects of the type_and_subtype '''
        first = True
        collectiontype = None        
        for id in ids:
            if first:
                collectiontype = Identifier.type_and_subtype(id)
                collection = self.get_collection(type_and_subtype)
                first = False
            if not collection.find_key(id):
                assert "id not found in collection"  
            if collectiontype != Identifier.type_and_subtype(id):
                assert "mixed types not allowed in a collection"        
  
        return collection[id in ids]    
