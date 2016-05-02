from heppy.framework.analyzer import Analyzer
from heppy.papas.data.comparer import ParticlesComparer
from heppy.papas.data.history import History
from heppy.papas.data.pfevent import  PFEvent

class PapasParticlesComparer(Analyzer):
    ''' Unsophisticated testing Module that checks that two lists of sorted particles match
    '''
    def __init__(self, *args, **kwargs):
        super(PapasParticlesComparer, self).__init__(*args, **kwargs)
        self.particlesA_name =  self.cfg_ana.particlesA
        self.particlesB_name =  self.cfg_ana.particlesB
                
    def process(self, event): #think about if argument is correct
        ''' calls a particle comparer to compare two lists of pre-sorted particles
        arguments
            event: must contain baseline_particles (the original reconstruction from simulation)
                   and reconstructed_particles made from the new BlockBuilder approach
        '''
        #may well change how pfevent and history are organised
        #pfevent=PFEvent(event)
        #history=History(event.history_nodes, pfevent)
        ParticlesComparer(getattr(event,  self.particlesA_name),  getattr(event, self.particlesB_name))
                        
        pass
        