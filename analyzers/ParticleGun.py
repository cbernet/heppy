from framework.analyzer import Analyzer
from particles.particle import Particle

from ROOT import TLorentzVector

import random
import math

class ParticleGun( Analyzer ):
    """
    Random, single particle generator.

    #TODO add parameters and describe them here
    #TODO base class for particle generators?

    The list of particles is put in
    event.gen_particles
    """

    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(ParticleGun,self).__init__(cfg_ana, cfg_comp, looperName)

    def process(self, event):
        # for now, just shoot a photon
        lv = TLorentzVector(0, 20, 50, math.sqrt(20*20+50*50))
        photon = Particle(0, 22, lv)
        event.gen_particles = [photon]
