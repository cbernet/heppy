from heppy.papas.data.identifier import Identifier
from heppy.framework.event import Event


class PapasEvent(Event):
    ''' Contains all the papas event data eg smeared tracks, merged ecal clusters, reconstructed particles etc
        together with the history which descibes the linkages between the data
        The collections and history are required to match perfectly,
        ie if an identifier is used in the history it must also be in one of the collections and vice versa

        The collections dict object itself contains dicts of each object type, 
        eg the collections object might look something like:
        collections = { 'et':true_ecals,  'ht':true_hcals, 'ts':smeared_tracks, 
                         'pr' = reconstrcted_particles, 'br':reconstructed_blocks, ...}
        where true_ecals is a dict of true ecals etc
        
        Each object-type in the collections dict must be unique 
        eg all smeared_ecals in the papasevent must be stored as one single dict inside the collections.
        
        The type_and_subtype seen above is used to label the collections in the papasevent
        it is a two letter code formed out of 'type' + 'subtype'
        For example
          'pr' is particle that has reconstructed subtype
          'et' contains the true ecals 

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
    '''
    
    def __init__(self, iEv):
        super(PapasEvent, self).__init__(iEv)
        Identifier.reset()
        self.collections = dict()
        self.history = dict()    
        
    def add_collection(self, collection):
        '''Add a new collection into the PapasEvent. The collection should contain only one object type
           and only one collection of each type should be stored in the PapasEvent        
        '''
        #find all the type_and_subtypes in the incoming collection
        if len(collection) == 0:
            return
        types = set(map(Identifier.type_and_subtype, collection.keys()))
        if len(types) > 1:
            raise ValueError('More than one type')
        the_type = types.pop()
        if the_type in self.collections:
            raise ValueError('type already present')
        self.collections[the_type] = collection        
    
    def get_collection(self, type_and_subtype):
        return self.collections.get(type_and_subtype, {})

    def get_object(self, uid):
        '''get an object corresponding to a unique uid'''
        #I am still not sure about this
        #would it be better to let it fail when asking for something that does not exist like this:
        #    return self.get_collections(Identifier.type_and_subtype(uid))[uid]
        #
        collection = self.get_collection(Identifier.type_and_subtype(uid))
        if collection:
            return collection.get(uid, None)
        return None

    
