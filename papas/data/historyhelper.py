from heppy.papas.graphtools.DAG import Node, BreadthFirstSearchIterative, DAGFloodFill
from heppy.papas.data.identifier import Identifier

class HistoryHelper(object):
    '''   
       Object to assist with printing and reconstructing histories.
       It allows extraction of information from the papasevent
       
       Usage:
       hist = HistoryHelper(papasevent)
       print hist.summary_string_event()
          
       rec_particles = self.get_collection('pr').values()
       
       #select a reconstructed particle and see what simulated particles are linked to it
       uid = rec_particles.keys()[0].uniqueid
       sim_particles = self.get_matched_linked_collection(uid,'ps')
     
       #see also examples subroutine below
       
       #see also papasevent documentation for details of the labelling of collections
         eg 'pr' is a collections of particles that have been reconstructed
        
    '''    
    def __init__(self, papasevent):
        ''' arguments
           papasevent is a PapasEvent which contains collections and history. 
        '''
        self.history = papasevent.history
        self.papasevent = papasevent
        
        
    def event_ids(self): 
        ''' 
           returns all the ids in the event
        '''
        return self.history.keys();
    
    def get_linked_ids(self, id, direction="undirected"):
        '''
        returns all ids linked to a given id
        arguments:
            id = unique identifier
            direction = parents/children/undirected
        '''
        BFS = BreadthFirstSearchIterative(self.history[id], direction)
        return [v.get_value() for v in BFS.result] 
    
    def id_from_pretty(self, pretty):
        ''' Searches to find the true id given a pretty id string
            Not super efficient but OK for occasional use
            eg uid = self.id_from_pretty('et103')
        '''
        for id in self.ids():
            if Identifier.pretty(id) == pretty:
                return id
        return None
    
    def get_matched_ids(self, ids, typecode):
        ''' returns the subset of ids which have a typecode that matchs the typecode argument
            eg merged_ecal_ids = get_matched_ids(ids, 'em')
        '''
        return [id for id in ids if Identifier.type_code(id) == typecode]
    
    def get_collection(self, subtype):
        '''returns an entire collection of the given subtype
        '''
        return self.papasevent.get_collection(subtype)
        
    def get_matched_collection(self, ids, subtype):
        '''return a collection of objects of subtype using only those ids which have the selected subtype
           ids wich have a different subtype will be ignored.
        '''        
        matchids = self.get_matched_ids(ids, subtype)  
        maindict = self.get_collection(subtype)
        return { id: maindict[id] for id in matchids}
        
    def get_matched_linked_collection(self, id, subtype, direction="undirected"):
        '''Get all ids that are linked to the id and have the required subtype
         
        arguments:
        id  = unique identifier
        subtype = type of object (eg 'es')
        direction = "undirected"/"parents"/"children"
    
        '''
        ids = self.get_linked_ids(id)
        return self.get_matched_collection(ids, subtype)   
    
    def summary_string_ids(self, ids, types = ['pg', 'tt', 'ts', 'et', 'es', 'em', 'ht', 'hs', 'hm', 'pr'], 
                           labels = ["gen_particles","gen_tracks","tracks", "ecals", "smeared_ecals","gen_ecals","hcals", 
                                     "smeared_hcals","gen_hcals","rec_particles"]):
        ''' String to describe the components corresponding to the selected ids
        '''
        makestring=""
        for i in range(len(types)):
            objdict = self.get_matched_collection(ids, types[i])
            newlist = [v.__str__() for a, v in objdict.items()] 
            makestring = makestring + "\n" + labels[i].rjust(13, ' ') + ":"  +'\n              '.join(newlist)
        return makestring    
    
    def summary_string_event(self, types = ['pg', 'tt', 'ts', 'et', 'es', 'em', 'ht', 'hs', 'hm', 'pr'], 
                       labels = ["gen_particles","gen_tracks","tracks", "ecals", "smeared_ecals","gen_ecals","hcals", 
                      "smeared_hcals","gen_hcals","rec_particles"]):
        ''' String to describe the papas event
        '''
        ids = self.event_ids()
        return self.summary_string_ids(ids, types, labels)
    
    def summary_string_subgroups(self, top = None):
        ''' Divide the event into connected subgroups
            Produce a summary string for the biggest "top" subgroups
        '''
        subgraphs=self.get_history_subgroups()  
        result= "Subgroups: \n"
        if top is None:
            top = len(subgraphs)
        for i in range(top):   
            result = result +  "SubGroup " + str(i) +"\n" + self.summary_string_ids(subgraphs[i])
        return result    
    
    def get_history_subgroups(self): #get subgroups of linked nodes, largest subgroup first
        ''' Divide the event into connected subgroups 
            each subgroup is a list of ids
        '''        
        self.subgraphs = []
        for subgraphlist in DAGFloodFill(self.history).blocks: # change to subgraphs
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
        for id, gp in self.papasevent.get_collection('pg').iteritems():
            all_linked_ids = self.get_linked_ids(id) 
            rec_particles = self.get_matched_collection(all_linked_ids, 'pr')
            gen_particles = self.get_matched_collection(all_linked_ids, 'pg') #linked gen particles
            print self.summary_string_ids(all_linked_ids)
    
        #questions 1  & 3
        for rp in self.event.papasevent.get_collection('pr').values():
            if abs(rp.pdgid())>100 and rp.q() != 0: #charged hadron
                parent_ids= self.get_linked_ids(rp.uniqueid,"parents")
                smeared_ecals = self.get_matched_collection(parent_ids, 'es') 
                sim_particles = self.get_matched_linked_collection(rp.uniqueid,'ps')
    
            pass            
 
