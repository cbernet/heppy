'''Papas history helper'''
from heppy.papas.graphtools.DAG import BreadthFirstSearchIterative, DAGFloodFill
from heppy.papas.data.identifier import Identifier

class HistoryHelper(object):
    '''Tool to assist with printing, plotting and reconstructing histories.
       
       It allows extraction of information from the papasevent
       
       #Usage:
       hist = HistoryHelper(event.papasevent)
       print hist.summary_string_event()
       
       #extract a list of all reconstructed particles 
       rec_particles = event.papasevent.get_collection('pr').values()
       print rec_particles
       
       #find an id from the pretty name
       uid =hist.id_from_pretty("pg66")
       
       #or select a reconstructed particle 
       uid = rec_particles.keys()[0].uniqueid
       
       #and see what simulated particles are linked to it
       sim_particles = self.get_linked_collection(uid,'ps')
     
       #see also examples subroutine below
       self.examples()
       
       #see also papasevent documentation for details of the labelling of collections
       #  eg 'pr' is a collections of particles that have been reconstructed
        
    '''    
    def __init__(self, papasevent):
        ''' arguments
           @param papaseven: is a PapasEvent which contains collections and history. 
        '''
        self.history = papasevent.history
        self.papasevent = papasevent
        
        
    def event_ids(self): 
        ''' 
           returns all the ids in the event
        '''
        return self.history.keys()
    
    def get_linked_ids(self, uid, direction="undirected"):
        '''
        returns all ids linked to a given uid
        @param uid: unique identifier
        @param direction: parents/children/undirected
        '''
        BFS = BreadthFirstSearchIterative(self.history[uid], direction)
        return [v.get_value() for v in BFS.result] 

    def filter_ids(self, ids, type_and_subtype):
        ''' returns a filtered subset of ids which have a type_and_subtype that matchs the type_and_subtype argument
            eg merged_ecal_ids = filter_ids(ids, 'em')
            @param ids: a list of ids
            @param type_and_subtype: a two letter type and subtype eg 'es' for smeared ecal
        '''
        return [uid for uid in ids
                if Identifier.type_and_subtype(uid) == type_and_subtype]
    
    def id_from_pretty(self, pretty):
        ''' Searches to find the true id given a pretty id string
            Not super efficient but OK for occasional use
            eg uid = self.id_from_pretty('et103')
            @param: pretty is the easily readable name from the Identifier class which is shown in prints and plots eg 'et103'
        '''
        for uid in self.history.keys():
            if Identifier.pretty(uid) == pretty:
                return uid
        return None
        
    def get_collection(self, ids, type_and_subtype):
        '''return a collection of objects of type_and_subtype using only those ids
        which have the selected type_and_subtype
        ids wich have a different type_and_subtype will be ignored.
        
        @param ids: a list of ids
        @param type_and_subtype: a two letter type and subtype eg 'es' for smeared ecal
        '''          
        maindict = self.papasevent.get_collection(type_and_subtype)
        fids = self.filter_ids(ids, type_and_subtype) 
        if len(fids):
            return { uid: maindict[uid] for uid in fids }
        else:
            return dict()
        
    def get_linked_collection(self, uid, type_and_subtype, direction="undirected"):
        '''Get all ids that are linked to the uid and have the required
        type_and_subtype
        
        @param uid  = unique identifier
        @param type_and_subtype = type of object (eg 'es')
        @param direction = says what type of linkage to use "undirected"/"parents"/"children"
    
        '''
        ids = self.get_linked_ids(uid, direction)
        return self.get_collection(ids, type_and_subtype)   
    
    def summary_string_ids(self, ids, type_and_subtypes = ['pg', 'tt', 'ts', 'et', 'es', 'em', 'ht', 'hs', 'hm', 'pr'], 
                           labels = ["gen_particles","true_tracks","smeared_tracks", "true_ecals", "smeared_ecals","merged_ecals","true_hcals", 
                                     "smeared_hcals","merged_hcals","rec_particles"]):
        ''' String to describe the components corresponding to the selected ids
        @param ids: list of uniqueids in history
        @param type_and_subtypes: list of type_and_subtypes
                            defaults to ['pg', 'tt', 'ts', 'et', 'es', 'em', 'ht', 'hs', 'hm', 'pr']
        @param labels: list of string labels (matching the type_and_subtypes)
                 defaults to ["gen_particles","true_tracks","smeared_tracks", "true_ecals", "smeared_ecals","merged_ecals","true_hcals", 
                                     "smeared_hcals","merged_hcals","rec_particles"]
        '''
        if len(type_and_subtypes) != len(labels):
            raise(ValueError, "Inconsistent arguments to summary_string_ids")
        makestring=""
        for i in range(len(type_and_subtypes)):
            objdict = self.get_collection(ids, type_and_subtypes[i])
            newlist = [v.__str__() for  v in objdict.itervalues()] 
            makestring = makestring + "\n" + labels[i].rjust(13, ' ') + ":"  +'\n              '.join(newlist)
        return makestring    
    
    def summary_string_event(self, types = ['pg', 'tt', 'ts', 'et', 'es', 'em', 'ht', 'hs', 'hm', 'pr'], 
                       labels = ["gen_particles","true_tracks","smeared_tracks", "true_ecals", "smeared_ecals","merged_ecals","true_hcals", 
                                     "smeared_hcals","merged_hcals","rec_particles"]):
        ''' String to describe the papas event
        @type_and_subtypes: list of type_and_subtypes
        @labels: list of string labels (matching the type_and_subtypes)
        '''
        ids = self.event_ids()
        return self.summary_string_ids(ids, types, labels)
    
    def summary_string_subgroups(self, num_subgroups = None):
        ''' Divide the event into connected subgroups and produce a summary string for the biggest n subgroups
            @param: if specified the n largest subgroups will be printed, otherwise all subgroups
        '''
        subgraphs=self.get_history_subgroups()  
        result= "Subgroups: \n"
        if num_subgroups is None:
            num_subgroups = len(subgraphs)
        else:
            num_subgroups = min(num_subgroups, len(subgraphs))
        for i in range(num_subgroups):   
            result = result +  "\nSubGroup: " + str(i) +"\n" + self.summary_string_ids(subgraphs[i])
        return result    
    
    def get_history_subgroups(self): #get subgroups of linked nodes, largest subgroup first
        ''' Divide the event into connected subgroups 
            each subgroup is a list of ids
        '''        
        self.subgraphs = []
        for subgraphlist in DAGFloodFill(self.history).subgraphs:
            element_ids = [node.get_value() for node in subgraphlist]            
            self.subgraphs.append(sorted(element_ids, reverse = True)) 
        self.subgraphs.sort(key = len, reverse = True) #biggest to smallest group
        return self.subgraphs
    
    def examples(self) :
        '''Colins questions
        (1) Given a reconstructed charged hadron, what are the linked:-
                  smeared ecals/hcals/tracks etc
        (2) What reconstructed particles derive from a given generated particle?
        
        (3) Given a reconstructed particle, what simulated particles did it derive from?          
        eg generated charged hadron -> reconstructed photon + neutral hadron'''
        #question 2
        for uid, gen_particle in self.papasevent.get_collection('pg').iteritems():
            all_linked_ids = self.get_linked_ids(uid) 
            rec_particles = self.get_collection(all_linked_ids, 'pr')
            gen_particles = self.get_collection(all_linked_ids, 'pg') #linked gen particles
            print self.summary_string_ids(all_linked_ids)
    
        #questions 1  & 3
        for rec_particle in self.papasevent.get_collection('pr').values():
            if abs(rec_particle.pdgid())>100 and rec_particle.q() != 0: #charged hadron
                parent_ids= self.get_linked_ids(rec_particle.uniqueid,"parents")
                smeared_ecals = self.get_collection(parent_ids, 'es') 
                sim_particles = self.get_linked_collection(rec_particle.uniqueid,'ps')
            
 
