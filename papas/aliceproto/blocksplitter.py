from blockbuilder import BlockBuilder
class BlockSplitter(BlockBuilder):
    ''' BlockSplitter takes a block of particle flow element ids (clusters,tracks etc)
        and unlinks any specified edges. It then recalculates a new set of sub-blocks
        using the underlying BlockBuilder class
        
        Usage example:

            splitter = BlockSplitter(block, unlink_edges)
            for b in splitter.blocks.itervalues():
                print b
    '''
    def __init__(self,  block, unlink_edges, history_nodes=None):
        '''arguments:
        
        blocks  : dictionary of blocks {id1:block1, id2:block2, ...}
        unlink_edges : list of edges where a link is to be removed 
        history_nodes : an optional dictionary of history nodes which describes the parent child links between elements
    
        '''
        for edge in unlink_edges:
            edge.linked = False
        
        super(BlockSplitter, self).__init__(block.element_uniqueids, block.edges, history_nodes, block.pfevent)
        assert( isinstance(self.blocks,dict))
            
        #the new blocks are subblocks of the original block
        #so keep note of this in the history (at least for now)
        # nb in some cases the new block will be the same as the original block although
        # the edges will have changed (for python these changes will also be seen in
        # the original block)        
        if (self.history_nodes != None ):
            for subblockid in self.blocks.keys():
                #print "split" , block.uniqueid, subblockid
                self.history_nodes[block.uniqueid].add_child(history_nodes[subblockid])  
                 
        #set the original block to be inactive
        block.is_active = False 
        
    
       
            

        
                
        
         