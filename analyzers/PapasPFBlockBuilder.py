from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.aliceblockbuilder import BlockBuilder
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.aliceproto.getobject import GetObject


class PapasPFBlockBuilder(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFBlockBuilder, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        ecal = event.ecal_clusters
        hcal = event.hcal_clusters
        tracks = event.tracks
        distance = Distance()
        get_object = GetObject(event)
        
        blockbuilder = BlockBuilder( tracks, ecal, hcal, distance, get_object)
        print blockbuilder
            
        event.blocks = blockbuilder.blocks
        
