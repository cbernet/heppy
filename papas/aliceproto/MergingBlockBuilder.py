import itertools
from BlockBuilder import BlockBuilder
from edge import Edge
from DAG import Node
from heppy.papas.pfobjects import MergedSmearedCluster
from heppy.papas.pfobjects import MergedSmearedTrack

class MergingBlockBuilder(BlockBuilder):
    ''' EventBlockBuilder takes particle flow elements from an event (clusters,tracks etc)
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

            builder = EventBlockBuilder(pfevent, ruler)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self, layer, pfevent, ruler, history_nodes = None):
        '''
       pfevent is event structure inside which we find
         tracks is a dictionary : {id1:track1, id2:track2, ...}
         ecal is a dictionary : {id1:ecal1, id2:ecal2, ...}
         hcal is a dictionary : {id1:hcal1, id2:hcal2, ...}
         get_object() which allows a cluster or track to be found from its id
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
        self.merged =dict()

        # collate ids of cluster/tracks etc
        if layer=="tracker":
            uniqueids = list(pfevent.tracks.keys()) 
        elif layer=="ecal_in":
            uniqueids = list(pfevent.ecal_clusters.keys())         
        elif layer=="hcal_in":
            uniqueids = list(pfevent.hcal_clusters.keys())         
             
        
        # compute edges between each pair of nodes
        edges = dict()
        for id1, id2 in itertools.combinations(uniqueids,2):
            edge=self._make_edge(id1,id2, ruler)
            #the edge object is added into the edges dictionary
            edges[edge.key] = edge
        
        #note we do note want the merging blocks to be part of the history   
        super(MergingBlockBuilder, self).__init__(uniqueids,edges,None, pfevent)
        
        self.history_nodes = history_nodes
        if history_nodes is None:
            self.history_nodes =  dict( (idt, Node(idt)) for idt in uniqueids )             
        
        if layer=="tracker":
            self._make_merged_tracks()
        else: 
            self._make_merged_clusters()
        
    def _make_merged_clusters(self) :
        for block in self.blocks.itervalues():
            if len(block.element_uniqueids)==1 :
                #no merging needed
                self.merged[block.element_uniqueids[0]]=self.pfevent.get_object(block.element_uniqueids[0])
            else: 
                supercluster = None
                for elemid in block.element_uniqueids :
                    thing=self.pfevent.get_object(elemid)
                    if supercluster is None:
                        supercluster = MergedSmearedCluster(thing)
                        self.merged[supercluster.uniqueid]=supercluster
                        if (self.history_nodes):
                            snode = Node(supercluster.uniqueid)
                            self.history_nodes[supercluster.uniqueid] = snode
                            #now add in the links between the block elements and the block into the history_nodes
                            self.history_nodes[elemid].add_child(snode)
                        continue
                    else: 
                        supercluster += thing
                        if (self.history_nodes):
                            self.history_nodes[elemid].add_child(snode)        
    def _make_merged_tracks(self) :
        for block in self.blocks.itervalues():
            supertrack = None
            for elemid in block.element_uniqueids :
                thing=self.pfevent.get_object(elemid)
                if supertrack is None:
                    supertrack = MergedSmearedTrack(thing)
                    self.merged[supertrack.uniqueid]=supertrack
                    if (self.history_nodes):
                        snode = Node(supertrack.uniqueid)
                        self.history_nodes[supertrack.uniqueid] = snode
                        #now add in the links between the block elements and the block into the history_nodes
                        self.history_nodes[elemid].add_child(snode)
                    continue
                else: 
                    supertrack += thing
                    if (self.history_nodes):
                                self.history_nodes[elemid].add_child(snode)        

    def _make_edge(self,id1,id2, ruler):
        ''' id1, id2 are the unique ids of the two items
            ruler is something that measures distance between two objects eg track and hcal
            (see Distance class for example)
            it should take the two objects as arguments and return a tuple
            of the form
                link_type = 'ecal_ecal', 'ecal_track' etc
                is_link = true/false
                distance = float
            an edge object is returned which contains the link_type, is_link (bool) and distance between the 
            objects. 
        '''
        #find the original items and pass to the ruler to get the distance info
        obj1 = self.pfevent.get_object(id1)
        obj2 = self.pfevent.get_object(id2)
        link_type, is_linked, distance = ruler(obj1,obj2) #some redundancy in link_type as both distance and Edge make link_type
                                                          #not sure which to get rid of
        
        #make the edge and add the edge into the dict 
        return Edge(id1,id2, is_linked, distance) 
        
    
