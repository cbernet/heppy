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
        
        self.tracksname =    self.cfg_ana.tracks;    
        self.ecalsname = self.cfg_ana.ecals; 
        self.hcalsname = self.cfg_ana.hcals;
        self.blocksname = self.cfg_ana.output_blocks;
        self.historyname = self.cfg_ana.input_history;
        self.outhistoryname = self.cfg_ana.output_history;
                
    def process(self, event):
        
        pfevent=PFEvent(event, self.tracksname,  self.ecalsname,  self.hcalsname,  self.blocksname) #or instead pass hcal, ecal ,track visibly? or somehow add the get_object to event?
        
        distance = Distance()
        
        history_nodes =  None
        if hasattr(event, self.historyname) :
            history_nodes = getattr(event,  self.historyname)
        blockbuilder = PFBlockBuilder(pfevent, distance, history_nodes )
        #print blockbuilder
            
        setattr(event, self.blocksname, blockbuilder.blocks)
        setattr(event,  self.outhistoryname,  blockbuilder.history_nodes)
        
        
        
