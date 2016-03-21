from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.ParticlesComparer import ParticlesComparer



class PapasParticlesComparer(Analyzer):
    ''' Testing Module that checks that two lists of sorted particles match
    '''
    def __init__(self, *args, **kwargs):
        super(PapasParticlesComparer, self).__init__(*args, **kwargs)
                
    def process(self, event):
        ''' Event must contain alice_particles and colin_particles
        '''
        #pfevent=PFEvent(event) #or instead pass hcal, ecal ,track visibly? or somehow add the get_object to event?
       
    
        ParticlesComparer(event.alice_particles,event.colin_particles)
        pass
        