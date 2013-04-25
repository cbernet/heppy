from framework.Analyzer import Analyzer
from particles.Particle import Particle

from ROOT import TLorentzVector

import random
import math

class ParticleGun( Analyzer ):
    
    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(ParticleGun,self).__init__(cfg_ana, cfg_comp, looperName)

    def process(self, event):
        # for now, just shoot a photon
        lv = TLorentzVector(0, 20, 50, math.sqrt(20*20+50*50))
        photon = Particle(0, 22, lv)
        
        #DEV need a way to specify what a processor takes, 
        # and what it produces. 
        # for example, generators produce a list of gen particles
        # and store them with the name particles. 
        event.put(self.name, 'particles', [photon])
        
        