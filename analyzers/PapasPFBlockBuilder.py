from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfblockbuilder import PFBlockBuilder
from heppy.papas.data.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance


class PapasPFBlockBuilder(Analyzer):
    ''' Module to construct blocks of connected clusters and tracks 
        particles will eventually be reconstructed from elements of a block
    '''
    def __init__(self, *args, **kwargs):
        super(PapasPFBlockBuilder, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        pfevent=PFEvent(event) #or instead pass hcal, ecal ,track visibly? or somehow add the get_object to event?
        
        distance = Distance()
    
        blockbuilder = PFBlockBuilder(pfevent, distance)
        #print blockbuilder
            
        event.blocks = blockbuilder.blocks
        event.history_nodes = blockbuilder.history_nodes
        
        
        
