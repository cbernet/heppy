import itertools
from blockbuilder import BlockBuilder
from edge import Edge

class EventBlockBuilder(BlockBuilder):
    ''' BlockBuilder takes a set of particle flow elements (clusters,tracks etc)
        and uses the distances between elements to construct a set of blocks
        Each element will end up in one (and only one block)
        Blocks retain information of the elements and the distances between elements
        The blocks can then be used for future particle reconstruction
        The ids must be unique and are expected to come from the Identifier class
        
        attributes:
        
        blocks  : dictionary of blocks {id1:block1, id2:block2, ...}
        history_nodes : dictionary of nodes that describe which elements are parents of which blocks 
                        if an existing history_nodes tree  eg one created during simulation
                        is passed to the BlockBuilder then
                        the additional history will be added into the exisiting history 
        nodes : dictionary of nodes which describes the distances/links between elements
                the nodes dictionary will be used to create the blocks
    
        
        Usage example:

            builder = BlockBuilder(tracks, ecal, hcal,ruler,get_object)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self,  pfevent, ruler, history_nodes = None):
        '''
       pfevent is event structure inside which we find
         tracks is a dictionary : {id1:track1, id2:track2, ...}
         ecal is a dictionary : {id1:ecal1, id2:ecal2, ...}
         hcal is a dictionary : {id1:hcal1, id2:hcal2, ...}
       ruler is something that measures distance between two objects eg track and hcal
            (see Distance class for example)
            it should take the two objects as arguments and return a tuple
            of the form
                link_type = 'ecal_ecal', 'ecal_track' etc
                is_link = true/false
                distance = float
        hist_nodes is an optional dictionary of Nodes : { id:Node1, id: Node2 etc}
            it could for example contain the simulation history nodes
            A Node contains the id of an item (cluster, track, particle etc)
            and says what it is linked to (its parents and children)
            if hist_nodes is provided it will be added to with the new block information
            If hist_nodes is not provided one will be created, it will contain nodes
            corresponding to each of the tracks, ecal etc and also for the blocks that
            are created by the event block builder.
        '''
        
        #given a unique id this can return the underying object
        self.pfevent = pfevent

        # collate all the ids of tracks and clusters
        uniqueids=[]
        uniqueids = list(pfevent.tracks.keys()) + list(pfevent.ecal_clusters.keys()) + list(pfevent.hcal_clusters.keys()) 
        
        
        # compute edges between each pair of nodes
        edges = dict()
        for id1, id2 in itertools.combinations(uniqueids,2) :
            edge=self._make_edge(id1,id2, ruler)
            #the edge object is added into the edges dictionary
            edges[edge.key] = edge
            
        super(EventBlockBuilder, self).__init__(uniqueids,edges,history_nodes, pfevent)

    
    
    def _make_edge(self,id1,id2, ruler):
        ''' id1, id2 are the unique ids of the two items
            an edge object is returned which contains the link_type, is_link (bool) and distance between the 
            objects. 
        '''
        #find the original items and pass to the ruler to get the distance info
        obj1 = self.pfevent.get_object(id1)
        obj2 = self.pfevent.get_object(id2)
        link_type, is_linked, distance = ruler(obj1,obj2)
        
        #make the edge and add the edge into the dict 
        return Edge(id1,id2, link_type,is_linked, distance) 
        
    
