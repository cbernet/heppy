from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.pfreconstructor import PFReconstructor
from heppy.papas.aliceproto.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.aliceproto.getobject import GetObject


class PapasPFReconstructor(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFReconstructor, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        reconstructed = PFReconstructor(event)
        event.reconstructed_particles= sorted( reconstructed.particles,
                            key = lambda ptc: ptc.e(), reverse=True)
        event.history_nodes=reconstructed.history_nodes
        pass
        