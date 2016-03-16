import itertools

from DAG import Node, BreadthFirstSearchIterative, DAGFloodFill
from heppy.papas.aliceproto.identifier import Identifier
from edge import Edge    
from blockbuilder import PFBlock      


class BlockBuilder(object):
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
    def __init__(self,  pfevent, ruler, hist_nodes = None):
        '''
TODO update documentation
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
            are created by the block builder.
        '''
        
        #given a unique id this can return the underying object
        self.pfevent = pfevent

        # if the user does not specify an existing history tree,
        # start the tree with the identifiers of the provided tracks,
        # ecal and hcal clusters
        self.history_nodes = hist_nodes
        if self.history_nodes is None:
            self.history_nodes = dict(
                self._make_node_dict(pfevent.tracks).items() + 
                self._make_node_dict(pfevent.ecal_clusters).items() +
                self._make_node_dict(pfevent.hcal_clusters).items() )

        # build the block nodes (separate graph which will use distances between items to determine links)
        self.nodes = dict(
             self._make_node_dict(pfevent.tracks).items() + 
             self._make_node_dict(pfevent.ecal_clusters).items() +
             self._make_node_dict(pfevent.hcal_clusters).items() )
        
        # compute link properties between each pair of nodes
        self.edges = dict()
        for id1, id2 in itertools.combinations(self.nodes,2) :
            edge=self._make_edge(id1,id2, ruler)
            #the edge object is added into the edges dictionary
            self.edges[edge.key] = edge
            #add linkage info into the nodes dictionary
            if  edge.linked: #this is actually an undirected link - OK for undirected searches 
                self.nodes[id1].add_child(self.nodes[id2])            

        # build the blocks of connected nodes
        self.blocks = dict()
        self._make_blocks()

        
    def _make_node_dict(self, elems):  # this method is made private by the start _
        '''for a list of identifiers, return a dictionary
        {identifier: Node(identifier)}
        '''
        return dict( (idt, Node(idt)) for idt in elems )
    
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
        
    def _make_blocks (self) :
        ''' uses the DAGfloodfill algorithm in connection with the BlockBuilder nodes
            to work out which elements are connected
            Each set of connected elements will be used to make a new PFBlock
        ''' 
        for b in DAGFloodFill(self.nodes).blocks :
            rec_history_UIDs = [] 
            elem_descrips = []
            # NB the nodes that are found by FloodFill are the Nodes describing links between items
            # we acually want the blocks to contain the corresponding history nodes 
            # So, find the corresponding history nodes
            for e in b :
                rec_history_UIDs.append(e.get_value())
                #elem_descrips.append(self.get_object(e.get_value()).__str__())

            #now we can make the block
            block = PFBlock(rec_history_UIDs,  self.edges, self.pfevent) #pass the edgedata and extract the needed edge links for this block          
           
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] = block        
            
            #make a node for the block and add into the history Nodes
            blocknode = Node(block.uniqueid)
            self.history_nodes[block.uniqueid] = blocknode
            
            #now add in the links between the block elements and the block into the history_nodes
            for elemid in block.element_uniqueids :
                self.history_nodes[elemid].add_child(blocknode)            
            
            
    def __str__(self):
        descrip = "{ " 
        for block in self.blocks.iteritems() :
            descrip = descrip + block.__str__()
        descrip = descrip + "}\n"
        return descrip  
    
    def __repr__(self):
        return self.__str__()      


from copy import deepcopy
class BlockSplitter(object):
    ''' BlockSplitter takes a subset of particle flow elements (clusters,tracks etc)
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
    def __init__(self,  block, unlink_edges):
        '''
TODO update documentation
       
        '''
        
        #given a unique id this can return the underying object
        self.edges=block.edges
        self.pfevent=block.pfevent
        # build the block nodes (separate graph which will use distances between items to determine links)
        self.nodes = dict(self._make_node_dict(block.element_uniqueids ))
        self.history_nodes = block.pfevent.history_nodes
        
        for edge in unlink_edges :
            edge.linked=False
        
        for edge in block.edges.itervalues() :
            #add linkage info into the nodes dictionary
            if  edge.linked: #this is actually an undirected link - OK for undirected searches 
                self.nodes[edge.id1].add_child(self.nodes[edge.id2])            

        # build the blocks of connected nodes
        self.blocks = dict()
        self._make_blocks()        
        
        
        

        
    def _make_blocks (self) :
        ''' uses the DAGfloodfill algorithm in connection with the BlockBuilder nodes
            to work out which elements are connected
            Each set of connected elements will be used to make a new PFBlock
        ''' 
        for b in DAGFloodFill(self.nodes).blocks :
            rec_history_UIDs = [] 
            elem_descrips = []
            # NB the nodes that are found by FloodFill are the Nodes describing links between items
            # we acually want the blocks to contain the corresponding history nodes 
            # So, find the corresponding history nodes
            for e in b :
                rec_history_UIDs.append(e.get_value())
                #elem_descrips.append(self.get_object(e.get_value()).__str__())

            #now we can make the block
            block = PFBlock(rec_history_UIDs,  self.edges, self.pfevent) #pass the edgedata and extract the needed edge links for this block          
           
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] = block        
            
            #make a node for the block and add into the history Nodes
            if (block.pfevent.history_nodes != None) :
                blocknode = Node(block.uniqueid)
                self.history_nodes[block.uniqueid] = blocknode
            
            #now add in the links between the block elements and the block into the history_nodes
            for elemid in block.element_uniqueids :
                self.history_nodes[elemid].add_child(blocknode)            
            
    def _make_node_dict(self, elems):  # this method is made private by the start _
        '''for a list of identifiers, return a dictionary
        {identifier: Node(identifier)}
        '''
        return dict( (idt, Node(idt)) for idt in elems )   
                
    def __str__(self):
        descrip = "{ " 
        for block in self.blocks.iteritems() :
            descrip = descrip + block.__str__()
        descrip = descrip + "}\n"
        return descrip  
    
    def __repr__(self):
        return self.__str__()      
  
#
#What is the purpose of the class? 
#    describe interface, and in particular what are the# 
#    important attributes that the user can find in this class
#    give a usage example.$tell how to use the blocks (code fragment)
#
#    review all methods : pythonic name e.g. make_history_node 
#    think about what has to be private or exposed to the user
#    same for attributes

#describe what the method is doing.. here ok because constructor
#    describe what is expected for parameters, e.g. dictionary for tracks, ecal
#    hcal.
#    say also what method is returning.