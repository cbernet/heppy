from heppy.papas.data.identifier import Identifier
from heppy.framework.event import Event


class PapasEvent(Event):
    ''' Contains all the papas event data eg tracks, clusters, particles, blocks
        together with the hisotry whcih descibes the linkages between the data
        The collections and history are required to match perfectly,
        ie if in identifier is in the hostory it will be in one of the collections and vice versa

        The collections dict object contains dicts one dict per object type,
        eg all smeared_ecasl in the papasevent will be stored as one dict inside the collections.
        
        The type_code is used to label the collections in the papasevent
        it is a two letter code formed out of 'type' + 'subtype'
        For example
          'pr' is particle that has reconstructed subtype
          'es' contains ecals that are smeared

        Type codes
                      e = ecal
                      h = hcal
                      t = track
                      p = particle

        Subtype_codes are a single letter, current usage is:
            eg 
             'g' generated
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
                collectiontype = Identifier.type_code(id)
                if collectiontype in self.collections.keys():
                    assert "Collection Type must be unique"
                first = False
            if collectiontype != Identifier.type_code(id):
                assert "mixed types not allowed in a collection"
        self.collections[collectiontype] = collection
    
    def get_collection(self, type_code):
        return self.collections[type_code]
    
    def get_object(self, id):
        '''get an object corresponding to a unique id'''
        return self.collections[Identifier.type_code(id)][id]
    
    def get_objects(self, ids, type_code):
        ''' ids must all be of type type_code
        get a dict of objects of the type_code '''
        first = True
        collectiontype = None        
        for id in collection.iterkeys():
            if first:
                collectiontype = Identifier.type_code(id)
                first = False
            if collectiontype != Identifier.type_code(id):
                assert "mixed types not allowed in a collection"        
        
        return self.collections[type_code][id in ids]    

    #TODO check printout via event
    #def __str__(self):
        #header = 'PapasEvent:'
        #stripped_attrs = self.lines()
        #contents = pprint.pformat(stripped_attrs, indent=4)
        #return '\n'.join([header, contents])
        
        
    #def lines(self):
        ##approach copied from event.py and results used in printing this as part of 
        ##event - improvements likely to be needed
        #stripped_attrs = dict()
        #for name, value in {"tracks" : self.tracks ,
        #"gen tracks" :self.gen_tracks ,
        #"ecal_clusters": self.ecal_clusters ,
        #"hcal_clusters": self.hcal_clusters ,
        #"gen_ecals": self.gen_ecals ,
        #"gen_hcals": self.gen_hcals ,
        #"smeared_hcals": self.smeared_ecals ,
        #"smeared_hcals": self.smeared_hcals ,
        ##"history": self.history ,
        #"sim_particles": self.sim_particles ,
        #"gen_stable_particles": self.gen_stable_particles }.iteritems() :
        #stripped_attrs[name] = value
        #for name, value in stripped_attrs.iteritems():
        #if hasattr(value, '__len__') and len(value)>self.__class__.print_nstrip+1:
        ## taking the first 10 elements and converting to a python list 
        ## note that value could be a wrapped C++ vector
        #if isinstance(value, collections.Mapping):
        #entries = [entry for entry in value.iteritems()]
        #entries = entries[:self.__class__.print_nstrip]
        #entries
        #stripped_attrs[name] = dict(entries)
        #else:
        #stripped_attrs[name] = [ val for val in value[:self.__class__.print_nstrip] ]
        #stripped_attrs[name].append('...')
        #stripped_attrs[name].append(value[-1])    
        #return stripped_attrs
