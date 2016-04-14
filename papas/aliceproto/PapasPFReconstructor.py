from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.pfreconstructor import PFReconstructor
from heppy.papas.aliceproto.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.aliceproto.history import History

class PapasPFReconstructor(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasPFReconstructor, self).__init__(*args, **kwargs)
        self.detector = self.cfg_ana.detector
        self.reconstructed = PFReconstructor(self.detector, self.mainLogger)
                
    def process(self, event):
        ''' Calls the particle reconstruction algorithm and returns the 
           reconstructed paricles and updated history_nodes to the event object
           arguments:
                    event must contain blocks amde using BlockBuilder'''
        
        self.reconstructed.reconstruct(event)
        #for history to work we want a dict of particles
        event.reconstructed_particles = self.reconstructed.particles
        
        #hist = History(event.history_nodes,PFEvent(event))
        #for block in event.blocks:
        #    hist.summary_of_links(block)
        
        #for particle comparison we want a list of particles (instead of a dict) so that we can sort and compare
        event.reconstructed_particle_list = sorted( self.reconstructed.particles.values(),
                                                   key = lambda ptc: ptc.e(), reverse=True)
        event.history_nodes = self.reconstructed.history_nodes
        pass         