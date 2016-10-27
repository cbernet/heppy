import itertools
from blockbuilder import BlockBuilder
from heppy.papas.graphtools.edge import Edge
from heppy.papas.graphtools.DAG import Node

class PFBlockBuilder(BlockBuilder):
    ''' PFBlockBuilder takes particle flow elements from an event (clusters,tracks etc)
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

            builder = PFBlockBuilder(papasevent, ruler)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self, uniqueids, papasevent, ruler, subtype ='r'):
        '''
            uniqueids list of which ids from papasevent to build blocks out of
            papasevent contains the collections of objects, 
                                the history (if not found it will be created)
                                get_object() which allows a cluster or track to be found from its id
            ruler is something that measures distance between two objects eg track and hcal
                (see Distance class for example)
                it should take the two objects as arguments and return a tuple
                of the form
                    link_type = 'ecal_ecal', 'ecal_track' etc
                    is_link = true/false
                    distance = float
        '''
        uniqueids = sorted(uniqueids)
        self.papasevent = papasevent
        if self.papasevent.history is None:
            self.papasevent.history =  dict( (idt, Node(idt)) for idt in uniqueids )       
        
        # compute edges between each pair of nodes
        edges = dict()

        for id1 in uniqueids:
            for  id2 in uniqueids:
                if id1 < id2 :
                    edge=self._make_edge(id1,id2, ruler)
                    #the edge object is added into the edges dictionary
                    edges[edge.key] = edge

        #use the underlying BlockBuilder to construct the blocks        
        super(PFBlockBuilder, self).__init__(uniqueids, edges, self.papasevent.history, subtype = subtype)

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
        obj1 = self.papasevent.get_object(id1)
        obj2 = self.papasevent.get_object(id2)
        link_type, is_linked, distance = ruler(obj1,obj2) #some redundancy in link_type as both distance and Edge make link_type
                                                          #not sure which to get rid of
        #for the event we do not want ehal_hcal links
        if link_type == "ecal_hcal":
            is_linked = False
            
        #make the edge 
        return Edge(id1,id2, is_linked, distance) 
