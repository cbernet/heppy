from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.pfreconstructor import PFReconstructor
from heppy.papas.aliceproto.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.aliceproto.getobject import GetObject


class PapasPFReconstructor(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFReconstructor, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        #pfevent=PFEvent(event) #or instead pass hcal, ecal ,track visibly? or somehow add the get_object to event?
        
        
    
        reconstructed = PFReconstructor(event)
        
        