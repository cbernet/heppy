from heppy.framework.analyzer import Analyzer
from heppy.papas.pdt import particle_data
from heppy.particles.tlv.particle import Particle 
import  math
#import random

from ROOT import TLorentzVector

def particle(pdgid, theta, phi, energy   ):
    mass, charge = particle_data[pdgid]
    costheta = math.cos( theta)
    sintheta = math.sin( theta)
    tantheta = sintheta / costheta
    cosphi = math.cos(phi)
    sinphi = math.sin(phi)        
    momentum = math.sqrt(energy**2 - mass**2)
    tlv = TLorentzVector(momentum*sintheta*cosphi,
                         momentum*sintheta*sinphi,
                         momentum*costheta,
                         energy)
    return Particle(pdgid, charge, tlv) 
    

class Gun(Analyzer):
    
    def process(self, event):
        event.gen_particles = [particle(self.cfg_ana.pdgid, 
                                        self.cfg_ana.theta, 
                                        self.cfg_ana.phi,
                                        self.cfg_ana.energy
                                        )]
        event.gen_particles_stable = event.gen_particles
