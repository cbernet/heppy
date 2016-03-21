from blockbuilder import BlockBuilder
class BlockSplitter(BlockBuilder):
    ''' BlockSplitter takes a block of particle flow element ids (clusters,tracks etc)
        and unlinks any specified edges. It then recalculates a new set of sub-blocks
        using the underlying BlockBuilder class
        
        Usage example:

            splitter = BlockSplitter(block, unlink_edges)
            for b in splitter.blocks.itervalues() :
                print b
    '''
    def __init__(self,  block, unlink_edges, history_nodes=None):
        '''arguments:
        
        blocks  : dictionary of blocks {id1:block1, id2:block2, ...}
        unlink_edges : list of edges where a link is to be removed 
        history_nodes : an optional dictionary of history nodes which describes the parent child links between elements
    
        '''
        for edge in unlink_edges :
            print len(unlink_edges)
            print edge
            edge.linked = False
        
        super(BlockSplitter, self).__init__(block.element_uniqueids, block.edges, history_nodes, block.pfevent)
        assert( isinstance(self.blocks,dict))
            
        #the new blocks are subblocks of the original block
        #so keep note of this in the history (at least for now)
        if (self.history_nodes != None ) :
            for subblock in self.blocks.iteritems() :
                self.history_nodes[block.uniqueid].add_child(history_nodes[subblock])  
                 
        #set the original block to be inactive
        block.is_active = False 
        
        # nb in some cases the new block will be the same as the original block although
        # the edges will have changed (for python these changes will also be seen in
        #the original block)
        
            

        
                
        
         