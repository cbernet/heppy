from blockbuilder import BlockBuilder

class BlockSplitter(BlockBuilder):
    ''' BlockSplitter takes an exisiting block of particle flow element ids (clusters,tracks etc)
        and unlinks any specified edges. It then recalculates a new set of sub-blocks
        using the underlying BlockBuilder class
        
        Usage example:

            splitter = BlockSplitter(block, unlink_edges)
            for b in splitter.blocks.itervalues():
                print b
            
        Notes: (to be extended)
           if a block is split it will be marked as block.is_active=false
           as it will effectively be replaced by the new blocks after the split.
           ** explain how old block fits into history node ** 
    '''
    def __init__(self,  block, unlink_edges, history_nodes = None, subtype = 's'):
        '''arguments:
        
        blocks  : dictionary of blocks {id1:block1, id2:block2, ...}
        unlink_edges : list of edges where a link is to be removed 
        history_nodes : an optional dictionary of history nodes which describes the parent child links between elements
    
        '''
        for edge in unlink_edges:
            edge.linked = False
        
        super(BlockSplitter, self).__init__(block.element_uniqueids, block.edges, history_nodes, subtype = subtype)
        assert( isinstance(self.blocks,dict))
        
        
        #add in history link between block and splitblocks
        #check if history nodes exists
        if (history_nodes == None):
            return
        
        #find the node for the block        
        blocknode = self.history_nodes[block.uniqueid]
        
        #find or make a node for the particle            
        for splitblockid in self.blocks:
            snode = self.history_nodes[splitblockid]
            #link particle to the block            
            blocknode.add_child(snode)        
            
        #set the original block to be inactive
        block.is_active = False 
        
    
       
            

        
                
        
         