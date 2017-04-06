from heppy.papas.graphtools.DAG import Node, DAGFloodFill
from heppy.papas.pfalgo.pfblock import PFBlock
from heppy.papas.graphtools.subgraphbuilder import SubgraphBuilder
from heppy.utils.pdebug import pdebugger

        
class BlockBuilder(SubgraphBuilder):
    ''' BlockBuilder takes a set of identifiers and a dict of associated edges which have distance and link info
        It uses the distances between elements to construct a set of blocks
        Each element will end up in one (and only one block)
        Blocks retain information of the elements and the distances between elements
        The blocks can then be used for future particle reconstruction
        The ids must be unique and are expected to come from the Identifier class
        
        attributes:
        
        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance between two ids
        startindex : the index of the blocks collection into which the new blocks are to be added 
                (used to create Identifiers for new blocks)
        subtype :used when creating unique identifiers, normally 'r' reconstructed or 's' split
        history : dictionary of nodes that describe which elements are parents of which blocks 
                  it is provided so that the actions of the block builder can be recorded
        nodes : a set of nodes corresponding to the unique ids which is used to construct a graph
                and thus find distinct blocks
        blocks: the resulting blocks
    
        Usage example:
            builder = BlockBuilder(ids, edges, 0, 'r', history)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self, ids, edges, startindex, subtype, history = None,):
        '''
        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance/link between two ids
        startindex : the index of the blocks collection into which the new blocks are to be added (used to create Identifier)
        subtype :used when creating unique identifiers, normally 'r' reconstructed or 's' split
        history : dict of history nodes into which the history of the blockbuilder can be added
        '''
        self.history = history
        self.subtype = subtype
        self.startindex = startindex
        super(BlockBuilder, self).__init__(ids, edges)       

        # build the blocks of connected nodes
        self.blocks = dict()
        self._make_blocks()        
    
    def _make_blocks (self) :
        ''' uses the DAGfloodfill algorithm in connection with the BlockBuilder nodes
            to work out which elements are connected
            Each set of connected elements will be used to make a new PFBlock
        ''' 
        for subgraph in self.subgraphs:
            #make the block
            block = PFBlock(subgraph, self.edges, self.startindex + len(self.blocks), subtype=self.subtype)        
            pdebugger.info("Made {}".format(block))
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] = block        
            
            #make a node for the block and add into the history Nodes
            if (self.history != None):
                blocknode = Node(block.uniqueid)
                self.history[block.uniqueid] = blocknode
                #now add in the links between the block elements and the block into the history
                for elemid in block.element_uniqueids:
                    self.history[elemid].add_child(blocknode)

    def __str__(self):
        descrip = "{ "
        for block in sorted(blocks.keys(), reverse=True): #do largest blocks first          
            descrip = descrip + self.blocks[block].__str__() 
        descrip = descrip + "}\n"
        return descrip  
    
    def __repr__(self):
        return self.__str__()     