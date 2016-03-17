from heppy.framework.analyzer import Analyzer
from heppy.papas.aliceproto.ParticlesComparer import ParticlesComparer



class PapasParticlesComparer(Analyzer):

    def __init__(self, *args, **kwargs):
        super(PapasParticlesComparer, self).__init__(*args, **kwargs)
                
    def process(self, event):
        
        #pfevent=PFEvent(event) #or instead pass hcal, ecal ,track visibly? or somehow add the get_object to event?
        
        if(len(event.colin_particles)==3) :
            pass
    
        ParticlesComparer(event.alice_particles,event.colin_particles)
        pass
        