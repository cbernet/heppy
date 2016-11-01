from blockbuilder import BlockBuilder

class BlockSplitter(BlockBuilder):
    ''' BlockSplitter takes an exisiting block of particle flow element ids (clusters,tracks etc)
        and unlinks any specified edges. It then recalculates a new set of sub-blocks
        using the underlying BlockBuilder class
        
        Usage example:
            splitter = BlockSplitter(block, unlink_edges)
            for b in splitter.blocks.itervalues():
                print b
    '''
    def __init__(self, blockid,  blockids, edges, history = None, subtype = 's'):
        '''arguments:
        blockids  : list of ids in blck
        edges : list of edges  
        history : an optional dictionary of history nodes which describes the parent child links between elements
        '''
        super(BlockSplitter, self).__init__(blockids, edges, history, subtype = subtype)

        #add in history link between block and splitblocks
        #check if history nodes exists
        if (history == None):
            return
        
        #find the node for the original block        
        blocknode = self.history[blockid]   
        #link new split blocks to old block
        for splitblockid in self.blocks:
            snode = self.history[splitblockid]      
            blocknode.add_child(snode)        
    