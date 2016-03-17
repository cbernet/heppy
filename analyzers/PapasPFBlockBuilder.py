from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.eventblockbuilder import EventBlockBuilder
from heppy.papas.aliceproto.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.aliceproto.getobject import GetObject


class PapasPFBlockBuilder(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFBlockBuilder, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        pfevent=PFEvent(event) #or instead pass hcal, ecal ,track visibly? or somehow add the get_object to event?
        
        distance = Distance()
    
        blockbuilder = EventBlockBuilder( pfevent, distance)
        print blockbuilder
            
        event.blocks = blockbuilder.blocks
        event.history_nodes= blockbuilder.history_nodes
        
