from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.blockbuilder import BlockBuilder
        
class PapasPFBlockBuilder(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFBlockBuilder, self).__init__(*args, **kwargs)
                
    def process(self, event):
        ecal = event.ECALclusters
        hcal = event.HCALclusters
        tracks = event.tracks
        blockbuilder = BlockBuilder(tracks, ecal, hcal)
        event.blocks = blockbuilder.blocks
