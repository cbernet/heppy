from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.ParticlesComparer import ParticlesComparer



class PapasParticlesComparer(Analyzer):
    ''' Unsophisticated testing Module that checks that two lists of sorted particles match
    '''
    def __init__(self, *args, **kwargs):
        super(PapasParticlesComparer, self).__init__(*args, **kwargs)
                
    def process(self, event):
        ''' Event must contain baseline_particles (the original reconstruction from simulation)
            and reconstructed_particles made from the new BlockBuilder approach
        '''
    
        ParticlesComparer(event.reconstructed_particles,event.baseline_particles)
        pass
        