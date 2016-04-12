from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.comparer import ParticlesComparer
from heppy.papas.aliceproto.history import History
from heppy.papas.aliceproto.pfevent import PFEvent

class PapasParticlesComparer(Analyzer):
    ''' Unsophisticated testing Module that checks that two lists of sorted particles match
    '''
    def __init__(self, *args, **kwargs):
        super(PapasParticlesComparer, self).__init__(*args, **kwargs)
                
    def process(self, event): #think about if argument is correct
        ''' calls a particle comparer to compare two lists of pre-sorted particles
        arguments
            event: must contain baseline_particles (the original reconstruction from simulation)
                   and reconstructed_particles made from the new BlockBuilder approach
        '''
        #may well change how pfevent and history are organised
        pfevent=PFEvent(event)
        history=History(event.history_nodes, pfevent)
        ParticlesComparer(event.reconstructed_particle_list,event.baseline_particles,history)
        
        
        pass
        