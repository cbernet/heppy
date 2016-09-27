from heppy.framework.analyzer import Analyzer
from heppy.papas.pdt import particle_data
from heppy.papas.pfobjects import Particle
#from heppy.particles.fcc.particle import Particle
from heppy.utils.pdebug import pdebugger
import  math
import heppy.statistics.rrandom as random

from ROOT import TLorentzVector, TVector3

def fixed_particle(pdgid, theta, phi, energy   ):
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
    return Particle(pdgid, charge, tlv, Identifier.PFOBJECTTYPE.PARTICLE, subtype ='g') 
    
def particle(pdgid, thetamin, thetamax, ptmin, ptmax, flat_pt=False):
    mass, charge = particle_data[pdgid]
    theta = random.uniform(thetamin, thetamax)
    phi = random.uniform(-math.pi, math.pi)
    energy = random.uniform(ptmin, ptmax)
    costheta = math.cos(math.pi/2. - theta)
    sintheta = math.sin(math.pi/2. - theta)
    tantheta = sintheta / costheta
    cosphi = math.cos(phi)
    sinphi = math.sin(phi)        
    if flat_pt:
        pt = energy
        momentum = pt / sintheta
        energy = math.sqrt(momentum**2 + mass**2)
    else:
        momentum = math.sqrt(energy**2 - mass**2)
    tlv = TLorentzVector(momentum*sintheta*cosphi,
                         momentum*sintheta*sinphi,
                         momentum*costheta,
                         energy)
    vertex = TVector3()
    return Particle(tlv, vertex, charge, pdgid )     

class Gun(Analyzer):
    
    def beginLoop(self, setup):
        super(Gun, self).beginLoop(setup)
        #pdebugger.open("/Users/alice/work/Outputs/python_physics_debug_output.txt")
        #pdebugger.info("start")
        pass
    
        
    
    def process(self, event):
        #event.gen_particles = [particle(self.cfg_ana.pdgid, 
       #                                 self.cfg_ana.theta, 
       #                                 self.cfg_ana.phi,
       #                                 self.cfg_ana.energy
       #                                 )]
        event.gen_particles = [particle(self.cfg_ana.pdgid, 
                                                self.cfg_ana.thetamin,
                                                self.cfg_ana.thetamax,
                                                self.cfg_ana.ptmin,
                                                self.cfg_ana.ptmax,
                                                self.cfg_ana.flat_pt
                                                )]
        event.gen_particles_stable = event.gen_particles

    def write(self, setup):
        #pdebugger.info("closing\n")
        #pdebug.close()
        pass
        
    def endLoop(self, setup):
        super(Gun, self).endLoop(setup)
        #pdebugger.info("closing\n")
        pdebug.close() 