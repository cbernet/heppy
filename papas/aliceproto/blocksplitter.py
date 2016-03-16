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
            edge.linked=False
        
        super(BlockSplitter, self).__init__(block.element_uniqueids, block.edges, history_nodes, block.pfevent)
        
        #we need to remove(or downgrade) either the original block node which has been split up, 
        # however in some cases the "split" block may be identical to the original  block 
        # in this case drop the new block
        # nb check with colin about the edges being updated
              
        if (len(self.blocks) == 1) :
            self.blocks[0].is_active = False
            inactiveblocknode=self.history_nodes[self.blocks[0]]
        else :
            inactiveblocknode=self.history_nodes[block.uniqueid]  
            
       
        for node in history_nodes.itervalues() :
            node.remove_all_links_to(inactiveblocknode)
            
        #the new blocks are subblocks of the original block
        #so keep note of this in the history (at least for now)
        if (self.history_nodes != None and len(self.blocks)>1) :
            for subblock in self.blocks :
                self.history_nodes[block.uniqueid].add_child(history_nodes[subblock]) 
                
        
         