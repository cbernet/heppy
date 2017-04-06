from blockbuilder import BlockBuilder
from heppy.papas.graphtools.edge import Edge
from heppy.papas.graphtools.DAG import Node

class PFBlockBuilder(BlockBuilder):
    ''' PFBlockBuilder creates edges to describe distances between particle flow elements 
        taken from a papasevent (clusters,tracks etc)
        It uses the edges to construct a set of disconnected blocks
        Each element will end up in one (and only one block)
        Blocks retain information of the elements and the distances between elements
        The blocks can then be used for future particle reconstruction
        The ids must be unique and are expected to come from the Identifier class
        
        attributes:
        
        papasevent: This is a PapasEvent which contains the collections of objects, 
                                the history (if not found it will be created)
                                get_object() which allows a cluster or track to be found from its id
        
        Usage example:

            builder = PFBlockBuilder(papasevent, uniqueids, ruler)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self, papasevent, uniqueids, ruler, startindex=0, subtype='r'):
        '''
            papasevent a PapasEvent (see above)            
            uniqueids list of which ids from papasevent to build blocks out of
            ruler is something that measures distance between two objects eg track and hcal
                (see Distance class for example)
                it should take the two objects as arguments and return a tuple
                of the form
                    link_type = 'ecal_ecal', 'ecal_track' etc
                    is_link = true/false
                    distance = float
            startindex is the index number for this block within the collection of blocks being created
            subtype says which identifier subtype to use when creating new blocks eg 'r' reconstructed, 's' split
        '''
        self.papasevent = papasevent
        if self.papasevent.history is None:
            self.papasevent.history = dict((idt, Node(idt)) for idt in uniqueids)
        
        # compute edges between each pair of nodes
        edges = dict()

        for id1 in uniqueids:
            for  id2 in uniqueids:
                if id1 < id2 :
                    edge = self._make_edge(id1, id2, ruler)
                    #the edge object is added into the edges dictionary
                    edges[edge.key] = edge

        #use the underlying BlockBuilder to construct the blocks        
        super(PFBlockBuilder, self).__init__(uniqueids, edges, startindex, subtype, self.papasevent.history)

    def _make_edge(self, id1, id2, ruler):
        ''' id1, id2 are the unique ids of the two items
            ruler is something that measures distance between two objects eg track and hcal
            (see Distance class for example)
            it should take the two objects as arguments and return a tuple
            of the form
                link_type = 'ecal_ecal', 'ecal_track' etc
                is_link = true/false
                distance = float
            an edge object is returned which contains the link_type:
                is_link (bool) and distance between the objects. 
        '''
        #find the original items and pass to the ruler to get the distance info
        obj1 = self.papasevent.get_object(id1)
        obj2 = self.papasevent.get_object(id2)
        assert(obj1 and obj2 )
        link_type, is_linked, distance = ruler(obj1, obj2) #some redundancy in link_type as both distance and Edge make link_type
                                                          #not sure which to get rid of
        #for the event we do not want ehal_hcal links
        if link_type == "ecal_hcal":
            is_linked = False
            
        #make the edge 
        return Edge(id1, id2, is_linked, distance) 
